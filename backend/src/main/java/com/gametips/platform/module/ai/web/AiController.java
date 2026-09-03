package com.gametips.platform.module.ai.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.module.ai.domain.AiParseTask;
import com.gametips.platform.module.ai.domain.AiQaLog;
import com.gametips.platform.module.ai.service.AiParseService;
import com.gametips.platform.module.ai.service.AiQaService;
import com.gametips.platform.module.content.domain.Guide;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/ai")
@RequiredArgsConstructor
public class AiController {

    private final AiParseService aiParseService;
    private final AiQaService aiQaService;

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
}
