package com.gametips.platform.module.content.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.module.content.domain.Article;
import com.gametips.platform.module.content.domain.WikiEntry;
import com.gametips.platform.module.content.repository.ArticleRepository;
import com.gametips.platform.module.content.repository.WikiEntryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 资讯 / 百科只读接口（安全配置已放行 GET /api/v1/articles/** 与 /api/v1/wiki/**）。
 */
@RestController
@RequiredArgsConstructor
public class ContentReadController {

    private final ArticleRepository articleRepository;
    private final WikiEntryRepository wikiEntryRepository;

    @GetMapping("/api/v1/articles")
    public ApiResponse<List<Article>> articles(@RequestParam(required = false) Long gameId) {
        List<Article> items = gameId == null
                ? articleRepository.findTop20ByStatusOrderByPublishedAtDesc("PUBLISHED")
                : articleRepository.findTop20ByGameIdAndStatusOrderByPublishedAtDesc(gameId, "PUBLISHED");
        return ApiResponse.ok(items);
    }

    @GetMapping("/api/v1/articles/{id}")
    public ApiResponse<Article> article(@PathVariable Long id) {
        return articleRepository.findById(id)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.error(2001, "资讯不存在"));
    }

    @GetMapping("/api/v1/wiki/{gameId}")
    public ApiResponse<List<WikiEntry>> wiki(@PathVariable Long gameId) {
        return ApiResponse.ok(wikiEntryRepository.findTop20ByGameIdOrderByLastUpdatedDesc(gameId));
    }
}
