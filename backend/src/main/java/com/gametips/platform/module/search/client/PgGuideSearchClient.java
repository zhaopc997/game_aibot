package com.gametips.platform.module.search.client;

import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Component;

/**
 * PostgreSQL ILIKE 降级实现（默认，无需 ES 环境）。
 */
@Component
@RequiredArgsConstructor
@ConditionalOnProperty(name = "app.search.provider", havingValue = "pg", matchIfMissing = true)
public class PgGuideSearchClient implements GuideSearchClient {

    private final GuideRepository guideRepository;

    @Override
    public Page<Guide> search(String keyword, String tag, Long gameId, Pageable pageable) {
        return guideRepository.search(keyword, tag, gameId, GuideStatus.PUBLISHED.name(), pageable);
    }
}
