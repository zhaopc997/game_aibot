package com.gametips.platform.module.recommend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.util.Map;

/**
 * 行为上报请求（客户端埋点批量/单条上报）。
 */
public record BehaviorEvent(
        Long userId,
        @NotBlank String actionType,       // VIEW / SEARCH / LIKE / FAVORITE / COMMENT
        @NotBlank String targetType,       // guide / article / wiki / question
        @NotNull Long targetId,
        Map<String, Object> context
) {}
