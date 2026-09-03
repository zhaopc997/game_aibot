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

    public void index(Guide guide) {
        try {
            client.index(i -> i.index(properties.getElasticsearch().getIndex())
                    .id(String.valueOf(guide.getId()))
                    .document(toDocument(guide)));
        } catch (Exception e) {
            log.error("index guide {} failed", guide.getId(), e);
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
     * 全量重建：分页读取全部已发布攻略刷入索引。
     * 定时 6 小时执行一次；也可手动触发。
     */
    @Scheduled(fixedDelay = 6 * 60 * 60 * 1000L, initialDelay = 60_000L)
    public void fullRebuild() {
        int page = 0;
        int bulk = properties.getElasticsearch().getBulkSize();
        long total = 0;
        Page<Guide> result;
        do {
            result = guideRepository.findAll(PageRequest.of(page, bulk));
            List<Guide> guides = result.getContent();
            for (Guide g : guides) {
                index(g);
            }
            total += guides.size();
            page++;
        } while (result.hasNext());
        log.info("guide index full rebuild done, indexed={}", total);
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
