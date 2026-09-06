package com.gametips.platform.module.memory.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

/**
 * 一条对话消息。
 *
 * <p>短期记忆(Memory.Short)的载体,本骨架阶段用 List 存于内存;
 * V2 落库时映射 {@code agent_message} 表(见 architecture-v2 §6.1)。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConversationMessage {

    public enum Role { USER, ASSISTANT, SYSTEM, TOOL_RESULT }

    private UUID messageId;
    private UUID conversationId;
    private Role role;
    private String content;
    private Instant createdAt;
}
