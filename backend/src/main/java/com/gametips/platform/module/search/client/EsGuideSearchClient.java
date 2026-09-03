package com.gametips.platform.module.search.client;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.search.Hit;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.search.config.SearchProperties;
import com.gametips.platform.module.search.document.GuideDocument;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * Elasticsearch 搜索实现。需 ES 环境，通过 app.search.provider=elasticsearch 启用。
 */
@Slf4j
@Component
@RequiredArgsConstructor
@ConditionalOnProperty(name = "app.search.provider", havingValue = "elasticsearch")
public class EsGuideSearchClient implements GuideSearchClient {

    private final ElasticsearchClient client;
    private final SearchProperties properties;
    private final GuideRepository guideRepository;

    @Override
    public Page<Guide> search(String keyword, String tag, Long gameId, Pageable pageable) {
        try {
            SearchResponse<GuideDocument> response = client.search(s -> s
                            .index(properties.getElasticsearch().getIndex())
                            .from((int) pageable.getOffset())
                            .size(pageable.getPageSize())
                            .query(q -> q.bool(b -> {
                                b.must(m -> m.multiMatch(mm -> mm
                                        .query(keyword == null ? "" : keyword)
                                        .fields("title^3", "summary")));
                                if (tag != null && !tag.isBlank()) {
                                    b.filter(f -> f.term(t -> t.field("tags").value(tag)));
                                }
                                if (gameId != null) {
                                    b.filter(f -> f.term(t -> t.field("gameId").value(gameId)));
                                }
                                b.filter(f -> f.term(t -> t.field("status").value(GuideStatus.PUBLISHED.name())));
                                return b;
                            })),
                    GuideDocument.class);

            List<Long> ids = response.hits().hits().stream()
                    .map(Hit::source)
                    .map(GuideDocument::getId)
                    .toList();
            List<Guide> guides = guideRepository.findAllById(ids);
            return new PageImpl<>(guides, pageable, response.hits().total() == null ? 0 : response.hits().total().value());
        } catch (Exception e) {
            log.error("es search failed, fallback to empty", e);
            return new PageImpl<>(List.of(), pageable, 0);
        }
    }
}
