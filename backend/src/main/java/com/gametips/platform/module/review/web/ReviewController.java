package com.gametips.platform.module.review.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.review.domain.ContentReview;
import com.gametips.platform.module.review.domain.ReviewStatus;
import com.gametips.platform.module.review.service.ContentReviewService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/reviews")
@RequiredArgsConstructor
public class ReviewController {

    private final ContentReviewService reviewService;

    /**
     * 内容提交审核（作者/系统调用）。返回审核结果。
     */
    @PostMapping("/submit")
    public ApiResponse<ContentReview> submit(@RequestParam String targetType,
                                             @RequestParam Long targetId,
                                             @RequestParam(required = false) String text) {
        return ApiResponse.ok(reviewService.submit(targetType, targetId, text));
    }

    @PreAuthorize("hasAnyRole('MODERATOR','ADMIN')")
    @GetMapping("/queue")
    public ApiResponse<List<ContentReview>> queue() {
        return ApiResponse.ok(reviewService.humanQueue());
    }

    @PreAuthorize("hasAnyRole('MODERATOR','ADMIN')")
    @PostMapping("/{reviewId}/decision")
    public ApiResponse<ContentReview> decide(@PathVariable Long reviewId,
                                             @RequestBody Map<String, String> body) {
        ReviewStatus decision = ReviewStatus.valueOf(body.get("decision"));
        return ApiResponse.ok(reviewService.review(reviewId, decision, CurrentUser.userId(), body.get("reason")));
    }
}
