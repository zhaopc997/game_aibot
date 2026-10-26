package com.gametips.platform;

import com.gametips.platform.module.review.domain.RiskLevel;
import com.gametips.platform.module.review.service.ContentReviewService;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class ContentReviewServiceTest {

    private final ContentReviewService service = new ContentReviewService(null, null, null);

    @Test
    void shouldClassifyLowRiskWithoutSensitiveWords() {
        assertThat(service.machineCheck("正常攻略内容：开局选角色")).isEqualTo(RiskLevel.LOW);
    }

    @Test
    void shouldClassifyHighRiskWithMultipleSensitiveWords() {
        assertThat(service.machineCheck("外挂代练 赌博 色情")).isEqualTo(RiskLevel.HIGH);
    }

    @Test
    void shouldClassifyMediumRiskWithOneHit() {
        assertThat(service.machineCheck("推荐使用辅助外挂资源")).isEqualTo(RiskLevel.MEDIUM);
    }
}
