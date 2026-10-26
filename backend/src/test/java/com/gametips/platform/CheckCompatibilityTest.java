package com.gametips.platform;

import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.rag.tool.GuideSearchTools;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

/**
 * check_compatibility 的真实判定行为测试。
 *
 * <p>此前该方法恒返回 COMPATIBLE 且不查库，会让用户拿到过期攻略而不自知。
 */
class CheckCompatibilityTest {

    private GuideSearchTools tools(List<Guide> guides) {
        GuideRepository repo = mock(GuideRepository.class);
        for (Guide g : guides) {
            when(repo.findById(anyLong())).thenReturn(Optional.of(g));
        }
        GuideSearchTools t = new GuideSearchTools(null, repo);
        return t;
    }

    private Guide guide(long id, GuideStatus status, Long versionId) {
        Guide g = new Guide();
        g.setId(id);
        g.setStatus(status);
        g.setVersionId(versionId);
        return g;
    }

    @Test
    void shouldReportOutdatedWhenGuideStatusIsOutdated() {
        GuideSearchTools t = tools(List.of(guide(1L, GuideStatus.OUTDATED, 10L)));
        List<Map<String, Object>> res = t.checkCompatibility(List.of(1L), null);
        assertThat(res).hasSize(1);
        assertThat(res.get(0).get("status")).isEqualTo("OUTDATED");
        assertThat(res.get(0).get("note").toString()).contains("OUTDATED");
    }

    @Test
    void shouldReportUnpublishedWhenGuideIsDraft() {
        GuideSearchTools t = tools(List.of(guide(2L, GuideStatus.DRAFT, 10L)));
        List<Map<String, Object>> res = t.checkCompatibility(List.of(2L), null);
        assertThat(res.get(0).get("status")).isEqualTo("UNPUBLISHED");
    }

    @Test
    void shouldReportNotFoundWhenGuideMissing() {
        GuideSearchTools t = tools(List.of());
        List<Map<String, Object>> res = t.checkCompatibility(List.of(999L), null);
        assertThat(res.get(0).get("status")).isEqualTo("NOT_FOUND");
    }

    @Test
    void shouldReportVersionMismatchWhenVersionsDiffer() {
        GuideSearchTools t = tools(List.of(guide(3L, GuideStatus.PUBLISHED, 10L)));
        List<Map<String, Object>> res = t.checkCompatibility(List.of(3L), "20");
        assertThat(res.get(0).get("status")).isEqualTo("VERSION_MISMATCH");
    }

    @Test
    void shouldBeCompatibleWhenVersionsMatch() {
        GuideSearchTools t = tools(List.of(guide(4L, GuideStatus.PUBLISHED, 10L)));
        List<Map<String, Object>> res = t.checkCompatibility(List.of(4L), "10");
        assertThat(res.get(0).get("status")).isEqualTo("COMPATIBLE");
    }

    @Test
    void shouldTreatMissingVersionAsCompatible() {
        GuideSearchTools t = tools(List.of(guide(5L, GuideStatus.PUBLISHED, null)));
        List<Map<String, Object>> res = t.checkCompatibility(List.of(5L), null);
        assertThat(res.get(0).get("status")).isEqualTo("COMPATIBLE");
    }

    @Test
    void shouldReturnEmptyForEmptyInput() {
        GuideSearchTools t = tools(List.of());
        assertThat(t.checkCompatibility(List.of(), "10")).isEmpty();
    }
}