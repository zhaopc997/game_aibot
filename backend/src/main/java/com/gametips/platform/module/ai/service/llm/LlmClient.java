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
}
