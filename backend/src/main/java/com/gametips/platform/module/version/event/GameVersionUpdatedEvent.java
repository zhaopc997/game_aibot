package com.gametips.platform.module.version.event;

/**
 * 游戏版本更新事件。
 * 触发：将相关攻略标记为 PENDING_VERIFICATION 并通知作者。
 */
public record GameVersionUpdatedEvent(Long gameId, Long gameVersionId, String newVersionNumber) {}
