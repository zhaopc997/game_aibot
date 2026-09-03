package com.gametips.platform.module.ai.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 大模型输出格式校验（简易 JSON Schema 校验）与降级策略。
 * 校验失败时降级为模板匹配，保证任务不直接失败。
 */
@Slf4j
@Component
public class AiContentValidator {

    private static final String SCHEMA_VERSION = "1.0";

    /**
     * 校验并规整 AI 输出。返回规整后的 content；若结构非法则降级生成最小结构。
     */
    public Map<String, Object> validateAndNormalize(Map<String, Object> raw) {
        if (raw == null) {
            return fallback();
        }
        Object stepsObj = raw.get("steps");
        List<?> steps = (stepsObj instanceof List<?> l) ? l : null;
        if (steps == null || steps.isEmpty()) {
            return fallback();
        }

        List<Map<String, Object>> normalizedSteps = new ArrayList<>();
        int id = 1;
        for (Object s : steps) {
            if (s instanceof Map<?, ?> m) {
                Map<String, Object> step = new HashMap<>();
                step.put("step_id", id++);
                step.put("title", strOf(m.get("title"), "步骤" + (id - 1)));
                step.put("description", strOf(m.get("description"), ""));
                step.put("images", m.get("images") instanceof List<?> il ? il : List.of());
                step.put("video", strOf(m.get("video"), null));
                step.put("conditions", m.get("conditions") instanceof List<?> cl ? cl : List.of());
                step.put("tools", m.get("tools") instanceof List<?> tl ? tl : List.of());
                normalizedSteps.add(step);
            }
        }
        if (normalizedSteps.isEmpty()) {
            return fallback();
        }
        Map<String, Object> content = new HashMap<>();
        content.put("schema_version", SCHEMA_VERSION);
        content.put("steps", normalizedSteps);
        return content;
    }

    private String strOf(Object o, String def) {
        return o == null ? def : o.toString();
    }

    /**
     * 降级：生成空结构，供人工编辑。
     */
    public Map<String, Object> fallback() {
        Map<String, Object> step = new HashMap<>();
        step.put("step_id", 1);
        step.put("title", "待整理");
        step.put("description", "AI 解析结果格式异常，已降级为空模板，请人工编辑。");
        step.put("images", List.of());
        step.put("video", "");
        step.put("conditions", List.of());
        step.put("tools", List.of());
        Map<String, Object> content = new HashMap<>();
        content.put("schema_version", SCHEMA_VERSION);
        content.put("steps", List.of(step));
        return content;
    }
}
