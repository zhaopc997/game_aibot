package com.gametips.platform.module.agent.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

/**
 * Agent Chat 入参(V2 architecture §5.1)。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatRequest {

    /** 会话 ID;为空则由服务端生成 */
    private UUID conversationId;

    /** 用户消息 */
    @NotBlank
    @Size(max = 2000)
    private String message;

    /** 是否流式(骨架阶段忽略,留位) */
    private Boolean stream;
}
