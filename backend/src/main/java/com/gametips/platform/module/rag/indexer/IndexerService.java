package com.gametips.platform.module.rag.indexer;

import com.gametips.platform.module.rag.client.EmbeddingClient;
import com.gametips.platform.module.rag.config.RagProperties;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.repository.GuideRepository;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.elasticsearch.client.elc.NativeQuery;
import org.springframework.data.elasticsearch.client.elc.NativeQueryBuilder;
import org.springframework.data.elasticsearch.core.ElasticsearchOperations;
import org.springframework.data.elasticsearch.core.IndexOperations;
import org.springframework.data.elasticsearch.core.SearchHit;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.data.elasticsearch.core.mapping.IndexCoordinates;
import org.springframework.data.elasticsearch.core.query.IndexQueryBuilder;
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

    private final IndexCoordinates index = IndexCoordinates.of("guide_chunks");

    /** 启动时确保索引存在(创建 + mapping 同步) */
    @PostConstruct
    public void ensureIndex() {
        try {
            IndexOperations ops = esOps.indexOps(GuideChunkDoc.class);
            if (!ops.exists()) {
                ops.create();
                ops.putMapping(ops.createMapping(GuideChunkDoc.class));
                log.info("[indexer] 创建索引 guide_chunks");
            } else {
                log.info("[indexer] 索引 guide_chunks 已存在");
            }
        } catch (Exception e) {
            log.warn("[indexer] 索引初始化失败(ES 未启动?): {}", e.getMessage());
        }
    }

    /**
     * 全量重建索引:删旧 → 重灌。
     * 给管理后台/初次部署用。
     */
    @Transactional(readOnly = true)
    public int rebuildAll() {
        log.info("[indexer] 开始全量重建索引…");
        // 索引由 ElasticsearchIndexBootstrap 在启动时建好(含 ngram analyzer),
        // 这里灌数据,不动 mapping(否则会覆盖 bootstrap 的 ngram analyzer)。
        List<Guide> all = guideRepository.findAll();
        int ok = 0;
        for (Guide g : all) {
            if (indexOne(g)) ok++;
        }
        log.info("[indexer] 全量重建完成,共 {} 篇", ok);
        return ok;
    }

    /** 索引单篇(供 Admin 后台新增/更新 guide 时调用,V2 阶段先不接,只走全量) */
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
        // steps JSON 解析
        try {
            if (g.getContent() != null) {
                Map<String, Object> c = g.getContent();
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> steps = (List<Map<String, Object>>) c.get("steps");
                if (steps != null) {
                    for (Map<String, Object> s : steps) {
                        Object t = s.get("title");
                        if (t != null) sb.append("· ").append(t).append('\n');
                    }
                }
            }
        } catch (Exception ignore) { /* steps 结构异常时忽略 */ }
        return sb.toString();
    }
}
