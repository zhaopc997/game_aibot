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
                                if (keyword != null && !keyword.isBlank()) {
                                    b.must(m -> m.multiMatch(mm -> mm
                                            .query(keyword)
                                            .fields("title^3", "summary")));
                                } else {
                                    b.must(m -> m.matchAll(ma -> ma));
                                }
                                if (tag != null && !tag.isBlank()) {
                                    // 用 .keyword 子字段做精确匹配：
                                    // status/tags 在索引中是 text 类型（会被小写化），
                                    // 而 term 查询不做归一化，直接查大写枚举值必然 0 命中。
                                    b.filter(f -> f.term(t -> t.field("tags.keyword").value(tag)));
                                }
                                if (gameId != null) {
                                    b.filter(f -> f.term(t -> t.field("gameId").value(gameId)));
                                }
                                b.filter(f -> f.term(t -> t
                                        .field("status.keyword")
                                        .value(GuideStatus.PUBLISHED.name())));
                                return b;
                            })),
                    GuideDocument.class);

            List<Long> ids = response.hits().hits().stream()
                    .map(Hit::source)
                    .map(GuideDocument::getId)
                    .toList();
            // 用 findAllById 回表取完整实体；注意其返回顺序与入参不一致，
            // 这里按 ES 的相关性得分顺序重排，避免搜索结果乱序。
            List<Guide> found = guideRepository.findAllById(ids);
            List<Guide> guides = ids.stream()
                    .map(id -> found.stream().filter(g -> id.equals(g.getId())).findFirst().orElse(null))
                    .filter(java.util.Objects::nonNull)
                    .toList();
            return new PageImpl<>(guides, pageable,
                    response.hits().total() == null ? 0 : response.hits().total().value());
        } catch (Exception e) {
            log.error("es search failed, fallback to empty", e);
            return new PageImpl<>(List.of(), pageable, 0);
        }
    }
}
