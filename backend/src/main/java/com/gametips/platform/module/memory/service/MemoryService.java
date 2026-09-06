package com.gametips.platform.module.memory.service;

import com.gametips.platform.module.memory.dto.ConversationMessage;
import com.gametips.platform.module.memory.dto.PlayerPreference;

import java.util.List;
import java.util.UUID;

/**
 * Memory 模块对外门面(V2 architecture §4.5)。
 *
 * <p>骨架阶段拆成两个子接口便于后续拆分实现:
 * <ul>
 *   <li>{@link #shortTerm(UUID, ConversationMessage)} 短期记忆,Redis 滑动窗口</li>
 *   <li>长期记忆接口见 {@link PreferenceService}</li>
 * </ul>
 *
 * <p>设计原则:不暴露存储细节,Agent 通过此接口读写,不感知 Redis/PG。
 */
public interface MemoryService {

    /**
     * 追加一条消息到短期上下文。
     * @param conversationId 会话 ID
     * @param message       本轮消息(USER / ASSISTANT / TOOL_RESULT)
     * @return 追加后的最近 N 条(默认滑动窗口 10 轮,见 application.yml: agent.memory.short-window)
     */
    List<ConversationMessage> shortTerm(UUID conversationId, ConversationMessage message);

    /**
     * 读取短期上下文全部消息。
     */
    List<ConversationMessage> readShort(UUID conversationId);

    /**
     * 清空短期记忆(用户主动重置会话时)。
     */
    void clearShort(UUID conversationId);

    /**
     * 读取玩家长期偏好;骨架阶段返回空,真实读取从 user_game_profile.preference JSONB。
     */
    PlayerPreference loadPreference(Long userId);

    /**
     * 写入玩家长期偏好(由 record_player_preference Tool 调用)。
     */
    void savePreference(Long userId, PlayerPreference pref);
}
