package com.gametips.platform;

import com.gametips.platform.module.ai.service.AiContentValidator;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

class AiContentValidatorTest {

    private final AiContentValidator validator = new AiContentValidator();

    @Test
    void shouldNormalizeValidSteps() {
        Map<String, Object> raw = Map.of(
                "steps", List.of(
                        Map.of("title", "开局", "description", "选角色"),
                        Map.of("title", "中期", "description", "刷装备", "conditions", List.of("等级>30"))));
        Map<String, Object> content = validator.validateAndNormalize(raw);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> steps = (List<Map<String, Object>>) content.get("steps");
        assertThat(steps).hasSize(2);
        assertThat(steps.get(0).get("step_id")).isEqualTo(1);
        assertThat(steps.get(1).get("step_id")).isEqualTo(2);
        assertThat(steps.get(1).get("conditions")).asList().contains("等级>30");
    }

    @Test
    void shouldFallbackWhenStepsMissing() {
        Map<String, Object> raw = Map.of("foo", "bar");
        Map<String, Object> content = validator.validateAndNormalize(raw);
        assertThat((List<?>) content.get("steps")).isNotEmpty();
    }

    @Test
    void shouldFallbackWhenNull() {
        Map<String, Object> content = validator.validateAndNormalize(null);
        assertThat(content.get("steps")).isNotNull();
    }
}
