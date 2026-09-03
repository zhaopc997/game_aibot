package com.gametips.platform.module.content.service;

import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.search.client.GuideSearchClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

/**
 * 攻略搜索：委托给 GuideSearchClient。
 * 通过 app.search.provider 切换 PG ILIKE 降级 或 Elasticsearch。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class GuideSearchService {

    private final GuideSearchClient searchClient;

    public Page<Guide> search(String keyword, String tag, Long gameId, int page, int size) {
        Page<Guide> result = searchClient.search(keyword, tag, gameId, PageRequest.of(page, size));
        log.debug("guide search via {}, keyword={}, hits={}", searchClient.name(), keyword, result.getTotalElements());
        return result;
    }
}
