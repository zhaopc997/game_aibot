package com.gametips.platform.module.ai.service.llm;

import java.util.Map;

/**
 * 大模型客户端抽象。MVP 阶段使用 Mock 实现；
 * 接入真实模型（GPT-4o / Claude / 文心一言）时新增实现类即可。
 */
public interface LlmClient {

    /**
     * 解析攻略内容为结构化 JSON。
     *
     * @param sourceType 来源类型：BILI_VIDEO / WEB_POST / IMAGE
     * @param rawContent 提取到的原始文本/转录
     * @return 结构化攻略 JSON（{"steps": [...]} 等）
     */
    Map<String, Object> parseGuide(String sourceType, String rawContent);

    /**
     * 问答。
     */
    String chat(String question, String context);

    /**
     * 生成攻略草稿。
     */
    Map<String, Object> generateDraft(String notes);

    /**
     * 是否支持自主工具调用 (Function Calling / ReAct)。
     */
    default boolean supportsTools() {
        return false;
    }

    /**
     * 带工具调用的多轮对话。
     *
     * @param messages 多轮对话历史与当前提示（OpenAI 格式：role, content, tool_calls, tool_call_id 等）
     * @param tools    可选的工具集合 Schema
     * @return 包含最终文本答复或模型决定调用的工具列表
     */
    default LlmResponse chatWithTools(java.util.List<Map<String, Object>> messages, java.util.List<Map<String, Object>> tools) {
        String lastUser = "";
        StringBuilder ctx = new StringBuilder();
        if (messages != null) {
            for (Map<String, Object> m : messages) {
                String role = String.valueOf(m.get("role"));
                String content = String.valueOf(m.get("content"));
                if ("user".equals(role)) {
                    lastUser = content;
                } else if ("tool".equals(role) || "system".equals(role)) {
                    ctx.append(content).append("\n");
                }
            }
        }
        String ans = chat(lastUser, ctx.toString());
        return LlmResponse.builder().content(ans).toolCalls(java.util.List.of()).build();
    }
}
