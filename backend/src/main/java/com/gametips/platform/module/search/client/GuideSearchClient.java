package com.gametips.platform.module.search.client;

import com.gametips.platform.module.content.domain.Guide;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * 攻略搜索客户端抽象。
 * 实现：PgGuideSearchClient（ILIKE 降级）、EsGuideSearchClient（Elasticsearch）。
 */
public interface GuideSearchClient {

    Page<Guide> search(String keyword, String tag, Long gameId, Pageable pageable);

    /** 供应商名称，便于日志/监控 */
    default String name() {
        return getClass().getSimpleName();
    }
}
