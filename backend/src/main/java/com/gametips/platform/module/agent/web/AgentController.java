package com.gametips.platform.module.agent.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.agent.dto.ChatRequest;
import com.gametips.platform.module.agent.dto.ChatResponse;
import com.gametips.platform.module.agent.service.AgentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Agent HTTP 入口(V2 architecture §5.1)。
 *
 * <p>Hello World 阶段只实现 {@code POST /api/v1/agent/chat},
 * 流式/历史/中断等接口在 V2.1 补。
 */
@RestController
@RequestMapping("/api/v1/agent")
@RequiredArgsConstructor
public class AgentController {

    private final AgentService agentService;

    @PostMapping("/chat")
    public ApiResponse<ChatResponse> chat(@Valid @RequestBody ChatRequest req) {
        // 未登录也允许，userId 传 0
        Long userId = CurrentUser.userIdOrZero();
        return ApiResponse.ok(agentService.chat(userId, req));
    }

    @PostMapping(value = "/chat/stream", produces = org.springframework.http.MediaType.TEXT_EVENT_STREAM_VALUE)
    public org.springframework.web.servlet.mvc.method.annotation.SseEmitter chatStream(@Valid @RequestBody ChatRequest req) {
        Long userId = CurrentUser.userIdOrZero();
        return agentService.chatStream(userId, req);
    }
}
