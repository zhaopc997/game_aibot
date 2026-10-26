package com.gametips.platform.module.ai.service.llm;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 大模型交互响应结构体，支持内容文本或工具调用指令。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LlmResponse {
    /** 模型直接输出的文本答复 */
    private String content;

    /** 模型决定调用的工具列表，若为空则表示直接回答完毕 */
    @Builder.Default
    private List<LlmToolCall> toolCalls = List.of();

    /** 是否有工具调用待执行 */
    public boolean hasToolCalls() {
        return toolCalls != null && !toolCalls.isEmpty();
    }
}
