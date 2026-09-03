package com.gametips.platform.module.recommend.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.recommend.service.RecommendService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/recommendations")
@RequiredArgsConstructor
public class RecommendController {

    private final RecommendService recommendService;

    @GetMapping("/feed")
    public ApiResponse<List<Long>> feed(@RequestParam(defaultValue = "20") int limit) {
        return ApiResponse.ok(recommendService.feed(CurrentUser.userId(), limit));
    }

    @GetMapping("/guides")
    public ApiResponse<List<Long>> guides(@RequestParam Long gameId,
                                          @RequestParam(defaultValue = "10") int limit) {
        return ApiResponse.ok(recommendService.recommendByGame(CurrentUser.userId(), gameId, limit));
    }
}
