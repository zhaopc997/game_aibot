package com.gametips.platform.module.memory.service;

/**
 * 长期偏好子接口(可独立实现,便于将来只换长期存储)。
 *
 * <p>骨架阶段与 {@link MemoryService} 共用实现,真实场景下:
 * 短期走 Redis,长期走 PG user_game_profile.preference JSONB。
 */
public interface PreferenceService {

    /** 读玩家偏好;不存在返回空对象。 */
    com.gametips.platform.module.memory.dto.PlayerPreference load(Long userId);

    /** 写玩家偏好(全量覆盖,Agent 抽取后由该接口持久化)。 */
    void save(Long userId, com.gametips.platform.module.memory.dto.PlayerPreference pref);
}
