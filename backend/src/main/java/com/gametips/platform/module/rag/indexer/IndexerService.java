package com.gametips.platform.module.rag.indexer;

import com.gametips.platform.module.rag.client.EmbeddingClient;
import com.gametips.platform.module.rag.config.ElasticsearchIndexBootstrap;
import com.gametips.platform.module.rag.config.RagProperties;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.review.event.GuideReviewFinishedEvent;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.data.elasticsearch.client.elc.NativeQuery;
import org.springframework.data.elasticsearch.client.elc.NativeQueryBuilder;
import org.springframework.data.elasticsearch.core.ElasticsearchOperations;
import org.springframework.data.elasticsearch.core.IndexOperations;
import org.springframework.data.elasticsearch.core.SearchHit;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.data.elasticsearch.core.mapping.IndexCoordinates;
import org.springframework.data.elasticsearch.core.query.IndexQueryBuilder;
import org.springframework.data.elasticsearch.core.query.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * RAG 索引器(§4.4 architecture-v2)。
 *
 * 流程:
 *   1. 从 PG 拉所有 PUBLISHED 状态的 guide(V2 简化:DRAFT 也索引,但前端只展示 PUBLISHED)
 *   2. 每个 guide 转 1 个 chunk(title + summary + steps 拼成纯文本)
 *   3. 调 EmbeddingClient 得 dense vector(可选,API 未配时跳过)
 *   4. 用 ElasticsearchOperations 写入 guide_chunks 索引
 *
 * 索引设计:
 *   - id: guide_id(便于 upsert)
 *   - text: 全文(BM25 命中)
 *   - embedding: dense_vector dim=1024(KNN 命中)
 *   - game_id / version_id: filter
 *   - title / summary: 展示
 *   - source_url: 跳转
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class IndexerService {

    private final GuideRepository guideRepository;
    private final ElasticsearchOperations esOps;
    private final EmbeddingClient embeddingClient;
    private final RagProperties ragProps;
    private final ElasticsearchIndexBootstrap indexBootstrap;

    private final IndexCoordinates index = IndexCoordinates.of("guide_chunks");

    /** 启动时确保索引存在(含 ngram analyzer 与 mapping 同步) */
    @PostConstruct
    public void ensureIndex() {
        try {
            indexBootstrap.bootstrap();
        } catch (Exception e) {
            log.warn("[indexer] 索引初始化失败(ES 未启动?): {}", e.getMessage());
        }
    }

    /**
     * 启动后自愈：RAG 索引为空但库中有攻略时，自动全量重建。
     *
     * <p>为什么需要：{@link #rebuildAll()} 此前只能通过管理接口
     * {@code POST /api/v1/rag/reindex} 手动触发。于是每当
     * <ul>
     *   <li>做了数据迁移（新库有数据、索引仍为空）</li>
     *   <li>ES 数据卷被重建</li>
     * </ul>
     * 时，索引会长期保持 0 条，表现为 AI 助手对任何问题都回答
     * 「未找到相关攻略」，且<b>重启不会恢复</b>，排查时极易误判为模型问题。
     *
     * <p>这里做一次自动补偿，让系统可自愈；仅在索引确实为空时才触发，
     * 不会造成每次重启都全量重灌。
     */
    @EventListener(ApplicationReadyEvent.class)
    public void autoRebuildIfEmpty() {
        try {
            long docCount = esOps.count(Query.findAll(), index);
            long guideCount = guideRepository.count();
            // 条件用"索引落后于数据库"而非"索引为空"：
            // 批量导入攻略后（本项目实测从 30 篇增到 52 篇）索引会只覆盖旧数据，
            // 若只在为空时重建，新增攻略将永远搜不到，且没有任何报错。
            if (docCount < guideCount) {
                log.info("[indexer] RAG 索引 {} 条落后于库中 {} 篇攻略，自动触发全量重建…", docCount, guideCount);
                int ok = rebuildAll();
                log.info("[indexer] 自动重建完成，共写入 {} 篇", ok);
            } else {
                log.info("[indexer] RAG 索引现有 {} 条（库中 {} 篇攻略），无需重建", docCount, guideCount);
            }
        } catch (Exception e) {
            log.warn("[indexer] 启动自愈检查失败（ES 不可用？）: {}", e.getMessage());
        }
    }

    /**
     * 全量重建索引:删旧 → 重灌。
     * 给管理后台/初次部署用。
     */
    @Transactional(readOnly = true)
    public int rebuildAll() {
        log.info("[indexer] 开始全量重建索引…");
        indexBootstrap.bootstrap();
        List<Guide> all = guideRepository.findAll();
        int ok = 0;
        for (Guide g : all) {
            if (indexOne(g)) ok++;
        }
        log.info("[indexer] 全量重建完成,共 {} 篇", ok);
        return ok;
    }

    @EventListener
    public void onGuideReviewFinished(GuideReviewFinishedEvent event) {
        if (event.isPassed()) {
            guideRepository.findById(event.getGuideId()).ifPresent(guide -> {
                boolean ok = indexOne(guide);
                log.info("[indexer] 增量索引审核通过攻略 id={} title='{}' result={}",
                        guide.getId(), guide.getTitle(), ok);
            });
        } else {
            try {
                esOps.delete(String.valueOf(event.getGuideId()), index);
                log.info("[indexer] 审核未通过，移除索引 guide id={}", event.getGuideId());
            } catch (Exception e) {
                log.debug("[indexer] 移除索引忽略异常: {}", e.getMessage());
            }
        }
    }

    /** 索引单篇(供 Admin 审核通过或全量重建时调用) */
    public boolean indexOne(Guide g) {
        try {
            GuideChunkDoc doc = toDoc(g);
            esOps.index(new IndexQueryBuilder()
                    .withId(String.valueOf(g.getId()))
                    .withObject(doc)
                    .build(), index);
            return true;
        } catch (Exception e) {
            log.error("[indexer] 索引 guide id={} 失败: {}", g.getId(), e.getMessage());
            return false;
        }
    }

    private GuideChunkDoc toDoc(Guide g) {
        // 把 steps[] 展平为可读文本(每个 step title + images)
        String text = buildChunkText(g);

        GuideChunkDoc doc = new GuideChunkDoc();
        doc.setId(String.valueOf(g.getId()));
        doc.setGuideId(g.getId());
        doc.setGameId(g.getGameId());
        doc.setVersionId(g.getVersionId());
        doc.setTitle(g.getTitle());
        doc.setSummary(g.getSummary());
        doc.setText(text);
        doc.setStatus(g.getStatus() != null ? g.getStatus().name() : "DRAFT");
        doc.setTags(g.getTags() == null ? List.of() : g.getTags());
        doc.setUpdatedAt(g.getUpdatedAt() != null ? g.getUpdatedAt().toString() : null);

        // 来源 URL(查 content_source 表)
        doc.setSourceUrl(findFirstSourceUrl(g.getId()));

        // embedding(可选)
        if (embeddingClient.isEnabled()) {
            try {
                doc.setEmbedding(embeddingClient.embedOne(text));
            } catch (Exception e) {
                log.warn("[indexer] embed guide id={} 失败,降级无向量: {}", g.getId(), e.getMessage());
            }
        }
        return doc;
    }

    private String findFirstSourceUrl(Long guideId) {
        // 简单实现:这里用 JPA 二次查询;V2 阶段没显式 join 必要
        try {
            return guideRepository.findById(guideId)
                    .map(g -> "/guides/" + g.getId())  // 默认本地路径
                    .orElse(null);
        } catch (Exception e) {
            return null;
        }
    }

    private String buildChunkText(Guide g) {
        StringBuilder sb = new StringBuilder();
        sb.append(g.getTitle()).append('\n');
        if (g.getSummary() != null) sb.append(g.getSummary()).append('\n');
        // steps JSON 解析:标题与正文都要索引,否则搜"钟离怎么叠护盾"这类
        // 具体步骤内容命中不到(step.description 是攻略的实质内容)
        try {
            if (g.getContent() != null) {
                Map<String, Object> c = g.getContent();
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> steps = (List<Map<String, Object>>) c.get("steps");
                if (steps != null) {
                    for (Map<String, Object> s : steps) {
                        Object t = s.get("title");
                        if (t != null) sb.append("· ").append(t).append('\n');
                        Object d = s.get("description");
                        if (d != null && !d.toString().isBlank()) {
                            sb.append(indent(String.valueOf(d), MAX_STEP_DESC_LEN)).append('\n');
                        }
                    }
                }
            }
        } catch (Exception ignore) { /* steps 结构异常时忽略 */ }
        return sb.toString();
    }

    /** 单个 step 正文最多索引的字符数,防止超长文本撑爆索引。 */
    private static final int MAX_STEP_DESC_LEN = 600;

    private static String indent(String s, int max) {
        String trimmed = s.length() <= max ? s : s.substring(0, max) + "…";
        return "  " + trimmed.replace("\n", " ");
    }
}
