package com.gametips.platform.module.ai.service.llm;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Mock 大模型实现：演示管线，从原始文本按行切分生成结构化步骤。
 * 通过 app.ai.provider=mock 启用（默认）。
 */
@Slf4j
@Component
@ConditionalOnProperty(name = "app.ai.provider", havingValue = "mock", matchIfMissing = true)
public class MockLlmClient implements LlmClient {

    @Override
    public Map<String, Object> parseGuide(String sourceType, String rawContent) {
        log.info("[mock-llm] parsing {} source, {} chars", sourceType, rawContent.length());
        List<Map<String, Object>> steps = new ArrayList<>();
        String[] lines = rawContent.split("\n");
        int stepId = 1;
        for (String line : lines) {
            String t = line.trim();
            if (t.isEmpty()) continue;
            Map<String, Object> step = new HashMap<>();
            step.put("step_id", stepId++);
            step.put("title", t.length() > 50 ? t.substring(0, 50) : t);
            step.put("description", t);
            step.put("images", List.of());
            step.put("conditions", List.of());
            steps.add(step);
        }
        Map<String, Object> content = new HashMap<>();
        content.put("steps", steps);
        content.put("source_type", sourceType);
        return content;
    }

    @Override
    public String chat(String question, String context) {
        return "（Mock 回答）关于「" + question + "」：" + context;
    }

    @Override
    public Map<String, Object> generateDraft(String notes) {
        return parseGuide("NOTES", notes);
    }
}
