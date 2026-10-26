package com.gametips.platform.module.ai.service.llm;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * 大模型工具调用描述 (OpenAI Function Calling 标准结构)。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LlmToolCall {
    /** 调用标识符，如 call_123456 */
    private String id;
    /** 调用的工具函数名，如 simulate_build / search_guides */
    private String name;
    /** 反序列化后的参数键值对 */
    private Map<String, Object> arguments;
}
