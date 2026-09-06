package com.gametips.platform.module.agent.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Agent Chat 出参(V2 architecture §5.1 示例)。
 *
 * <p>骨架阶段:plan 步骤固定 2 步(search_guides → check_compatibility),
 * answer 是模板拼装,接 LLM 后改为真实生成。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponse {

    private UUID conversationId;
    private UUID messageId;
    private String answer;
    private List<PlanStep> plan;
    private List<SourceRef> sources;
    private Map<String, Object> meta;
    private boolean degraded;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PlanStep {
        private int stepId;
        private String tool;
        private String status;       // SUCCESS / FAILED / SKIPPED
        private long durationMs;
        private String summary;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SourceRef {
        private Long guideId;
        private String title;
        private String version;
        private String url;
    }
}
