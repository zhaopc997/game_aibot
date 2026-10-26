package com.gametips.platform.module.review.dto;

import java.time.Instant;

/**
 * 统一审核队列项：既包含 content_review 中待人工审核的，
 * 也包含 guide 表中 DRAFT/PENDING_REVIEW 但尚未生成审核记录的攻略。
 */
public record ReviewQueueItem(
        Long reviewId,          // content_review.id；guide 直接待审时为 null
        String targetType,      // guide / comment / article
        Long targetId,          // guide.id 等
        String title,           // 攻略标题
        String status,          // DRAFT / PENDING_REVIEW / NEED_HUMAN / ...
        String riskLevel,       // LOW / MEDIUM / HIGH
        String reason,          // 审核理由
        String createdAt,
        Instant reviewCreatedAt
) {}