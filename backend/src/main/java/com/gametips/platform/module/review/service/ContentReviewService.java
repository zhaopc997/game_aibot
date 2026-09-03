package com.gametips.platform.module.review.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.review.domain.ContentReview;
import com.gametips.platform.module.review.domain.ReviewStatus;
import com.gametips.platform.module.review.domain.RiskLevel;
import com.gametips.platform.module.review.repository.ContentReviewRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.Set;

/**
 * 内容审核流程：
 * 1. 创建审核任务，机器审核（敏感词命中）判定风险级别；
 * 2. LOW/MEDIUM 自动通过，HIGH 转入人工队列（NEED_HUMAN）；
 * 3. 人工复核 PASSED / REJECTED，并驱动攻略状态流转。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ContentReviewService {

    private static final Set<String> SENSITIVE_WORDS =
            Set.of("外挂", "代练", "私服", "赌博", "色情", "违禁");

    private final ContentReviewRepository reviewRepository;
    private final GuideRepository guideRepository;

    /**
     * 提交内容审核。目标状态为 PENDING_REVIEW 的内容被审核。
     * 返回审核结果（自动通过 or 待人工）。
     */
    @Transactional
    public ContentReview submit(String targetType, Long targetId, String textContent) {
        ContentReview review = new ContentReview();
        review.setTargetType(targetType);
        review.setTargetId(targetId);
        review.setRiskLevel(machineCheck(textContent));
        if (review.getRiskLevel() == RiskLevel.HIGH) {
            review.setStatus(ReviewStatus.NEED_HUMAN);
        } else {
            review.setStatus(ReviewStatus.PASSED);
            review.setReviewedAt(Instant.now());
            applyResult(targetType, targetId, true);
        }
        return reviewRepository.save(review);
    }

    /**
     * 机器审核：敏感词命中数决定风险级别。正式环境可接入第三方内容安全 API。
     */
    public RiskLevel machineCheck(String text) {
        if (text == null || text.isBlank()) {
            return RiskLevel.LOW;
        }
        long hits = SENSITIVE_WORDS.stream().filter(text::contains).count();
        if (hits >= 2) return RiskLevel.HIGH;
        if (hits == 1) return RiskLevel.MEDIUM;
        return RiskLevel.LOW;
    }

    public List<ContentReview> humanQueue() {
        return reviewRepository.findTop100ByStatusOrderByCreatedAtAsc(ReviewStatus.NEED_HUMAN);
    }

    @Transactional
    public ContentReview review(Long reviewId, ReviewStatus decision, Long reviewerId, String reason) {
        ContentReview review = reviewRepository.findById(reviewId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "审核任务不存在"));
        if (decision != ReviewStatus.PASSED && decision != ReviewStatus.REJECTED) {
            throw new BizException(ErrorCodes.PARAM_ERROR, "人工审核仅支持 PASSED/REJECTED");
        }
        review.setStatus(decision);
        review.setReviewerId(reviewerId);
        review.setReason(reason);
        review.setReviewedAt(Instant.now());
        applyResult(review.getTargetType(), review.getTargetId(), decision == ReviewStatus.PASSED);
        return reviewRepository.save(review);
    }

    /**
     * 审核结果应用到目标（MVP 仅支持 guide）：
     * 通过 → PUBLISHED；拒绝 → REJECTED。
     */
    private void applyResult(String targetType, Long targetId, boolean passed) {
        if (!"guide".equals(targetType)) {
            log.warn("unsupported review target type: {}", targetType);
            return;
        }
        Guide guide = guideRepository.findById(targetId).orElse(null);
        if (guide == null) {
            log.warn("guide {} not found for review", targetId);
            return;
        }
        guide.setStatus(passed ? GuideStatus.PUBLISHED : GuideStatus.REJECTED);
        guideRepository.save(guide);
    }
}
