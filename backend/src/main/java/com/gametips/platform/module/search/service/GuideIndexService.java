package com.gametips.platform.module.search.service;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.search.config.SearchProperties;
import com.gametips.platform.module.search.document.GuideDocument;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 攻略索引同步：全量重建（定时）+ 单条 upsert/删除（应用调用）。
 * 仅当 app.search.provider=elasticsearch 时启用。
 */
@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(name = "app.search.provider", havingValue = "elasticsearch")
public class GuideIndexService {

    private final ElasticsearchClient client;
    private final GuideRepository guideRepository;
    private final SearchProperties properties;

    /**
     * 写入单条攻略索引。
     *
     * @return true 表示写入成功
     */
    public boolean index(Guide guide) {
        try {
            client.index(i -> i.index(properties.getElasticsearch().getIndex())
                    .id(String.valueOf(guide.getId()))
                    .document(toDocument(guide)));
            return true;
        } catch (Exception e) {
            log.error("index guide {} failed", guide.getId(), e);
            return false;
        }
    }

    public void delete(Long id) {
        try {
            client.delete(d -> d.index(properties.getElasticsearch().getIndex())
                    .id(String.valueOf(id)));
        } catch (Exception e) {
            log.error("delete guide {} from index failed", id, e);
        }
    }

    /**
     * 监听攻略审核完成事件：审核通过立即增量写入搜索索引，审核失败立即从索引移除，
     * 解决搜索索引只能靠定时任务全量拉取导致的最多 6 小时延迟问题。
     */
    @org.springframework.context.event.EventListener
    public void onGuideReviewFinished(com.gametips.platform.module.review.event.GuideReviewFinishedEvent event) {
        if (event.isPassed()) {
            guideRepository.findById(event.getGuideId()).ifPresent(guide -> {
                if (index(guide)) {
                    log.info("[search-indexer] 攻略审核通过，实时写入搜索索引 guideId={}", guide.getId());
                }
            });
        } else {
            delete(event.getGuideId());
            log.info("[search-indexer] 攻略审核未通过，从搜索索引中移除 guideId={}", event.getGuideId());
        }
    }

    /**
     * 全量重建：分页读取全部已发布攻略刷入索引。
     * 定时 6 小时执行一次；也可手动触发。
     */
    @Scheduled(fixedDelay = 6 * 60 * 60 * 1000L, initialDelay = 60_000L)
    public void fullRebuild() {
        int page = 0;
        int bulk = properties.getElasticsearch().getBulkSize();
        long attempted = 0;
        long succeeded = 0;
        Page<Guide> result;
        do {
            result = guideRepository.findAll(PageRequest.of(page, bulk));
            List<Guide> guides = result.getContent();
            for (Guide g : guides) {
                if (index(g)) {
                    succeeded++;
                }
            }
            attempted += guides.size();
            page++;
        } while (result.hasNext());

        // 分别统计"尝试"与"成功"：只打印尝试条数会在全部失败时仍显示成功，
        // 从而掩盖故障（本项目曾因此让索引长期为 0 却无人察觉）。
        long failed = attempted - succeeded;
        if (failed == 0) {
            log.info("guide index full rebuild done, indexed={}", succeeded);
        } else {
            log.error("guide index full rebuild finished with failures: attempted={}, succeeded={}, failed={}. "
                    + "索引可能不完整，请检查上方 error 日志", attempted, succeeded, failed);
        }
    }

    private GuideDocument toDocument(Guide g) {
        GuideDocument d = new GuideDocument();
        d.setId(g.getId());
        d.setGameId(g.getGameId());
        d.setVersionId(g.getVersionId());
        d.setTitle(g.getTitle());
        d.setSummary(g.getSummary());
        d.setTags(g.getTags());
        d.setDifficulty(g.getDifficulty());
        d.setStatus(g.getStatus().name());
        d.setLikeCount(g.getLikeCount());
        d.setUsefulCount(g.getUsefulCount());
        d.setUpdatedAt(g.getUpdatedAt());
        return d;
    }
}
