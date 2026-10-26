package com.gametips.platform.module.ai.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.ai.domain.AiParseTask;
import com.gametips.platform.module.ai.domain.AiQaLog;
import com.gametips.platform.module.ai.service.AiGuideGenService;
import com.gametips.platform.module.ai.service.AiParseService;
import com.gametips.platform.module.ai.service.AiQaService;
import com.gametips.platform.module.content.domain.Guide;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ai")
@RequiredArgsConstructor
public class AiController {

    private final AiParseService aiParseService;
    private final AiQaService aiQaService;
    private final AiGuideGenService aiGuideGenService;

    @PostMapping("/parse")
    public ApiResponse<AiParseTask> parse(@RequestParam String sourceType,
                                          @RequestParam String sourceUrl) {
        return ApiResponse.ok(aiParseService.submit(sourceType, sourceUrl));
    }

    @GetMapping("/parse/{taskId}")
    public ApiResponse<AiParseTask> status(@PathVariable Long taskId) {
        return ApiResponse.ok(aiParseService.getStatus(taskId));
    }

    @PostMapping("/qa")
    public ApiResponse<AiQaLog> qa(@RequestBody Map<String, String> body) {
        return ApiResponse.ok(aiQaService.ask(body.get("question")));
    }

    @PostMapping("/generate-draft")
    public ApiResponse<Guide> generateDraft(@RequestBody Map<String, String> body) {
        return ApiResponse.ok(aiQaService.generateDraft(body.get("notes")));
    }

    /**
     * AI 图文攻略批量生成：为指定游戏生成 count 条图文攻略草稿（DRAFT）。
     * POST /api/v1/ai/generate-guides?gameId=2&count=10
     * 仅允许管理员触发，防止高并发调用产生高额 LLM 账单。
     * 可选参数 topic：指定单一主题生成（用于批次逐篇轮换），如 topic=新手入门
     */
    @PostMapping("/generate-guides")
    @PreAuthorize("hasRole('ADMIN')")
    public ApiResponse<List<Guide>> generateGuides(@RequestParam Long gameId,
                                                   @RequestParam(defaultValue = "10") int count,
                                                   @RequestParam(required = false) String topic) {
        if (topic != null && !topic.isBlank()) {
            return ApiResponse.ok(List.of(aiGuideGenService.generateByTopic(gameId, topic, CurrentUser.userId())));
        }
        return ApiResponse.ok(aiGuideGenService.generateForGame(gameId, count, CurrentUser.userId()));
    }

    /** 可用的攻略主题列表（供批次任务轮换）。 */
    @GetMapping("/guide-topics")
    public ApiResponse<List<String>> guideTopics() {
        return ApiResponse.ok(aiGuideGenService.topics());
    }
}
