package com.gametips.platform;

import com.gametips.platform.module.agent.dto.ChatRequest;
import com.gametips.platform.module.agent.dto.ChatResponse;
import com.gametips.platform.module.agent.service.AgentService;
import com.gametips.platform.module.ai.service.llm.LlmClient;
import com.gametips.platform.module.memory.dto.PlayerPreference;
import com.gametips.platform.module.memory.service.MemoryService;
import com.gametips.platform.module.rag.dto.RagHit;
import com.gametips.platform.module.tool.dto.ToolResult;
import com.gametips.platform.module.tool.registry.ToolRegistry;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class AgentServiceTest {

    @Test
    void chat_shouldSynthesizeAnswerViaLlm() {
        MemoryService memoryService = mock(MemoryService.class);
        ToolRegistry toolRegistry = mock(ToolRegistry.class);
        LlmClient llmClient = mock(LlmClient.class);

        when(memoryService.loadPreference(1L)).thenReturn(
                PlayerPreference.builder().playStyle("手残党 / 轮椅配队").build()
        );

        RagHit hit = RagHit.builder()
                .guideId(101L)
                .title("钟离圣遗物刷取指南")
                .version("4.2")
                .snippet("推荐千岩4件套，主词条生生生。")
                .url("/guides/101")
                .build();

        when(toolRegistry.invoke(eq("search_guides"), any()))
                .thenReturn(ToolResult.ok(List.of(hit), 10));
        when(toolRegistry.invoke(eq("check_compatibility"), any()))
                .thenReturn(ToolResult.ok(List.of(Map.of("status", "COMPATIBLE")), 5));

        when(llmClient.chat(any(), any()))
                .thenReturn("（AI 建议）根据 4.2 版本与千岩4件套，生生生即可轻松毕业。");

        AgentService agentService = new AgentService(memoryService, toolRegistry, llmClient);

        ChatRequest req = new ChatRequest();
        req.setMessage("钟离怎么配装？");

        ChatResponse resp = agentService.chat(1L, req);

        assertThat(resp.getAnswer()).contains("千岩4件套");
        assertThat(resp.getSources()).hasSize(1);
        assertThat(resp.getSources().get(0).getGuideId()).isEqualTo(101L);
        assertThat(resp.getPlan()).hasSize(3); // search_guides, check_compatibility, llm_synthesize
        assertThat(resp.getPlan().get(2).getTool()).isEqualTo("llm_synthesize");
        assertThat(resp.getPlan().get(2).getStatus()).isEqualTo("SUCCESS");
    }

    @Test
    void chat_shouldFallbackGracefullyWhenLlmFails() {
        MemoryService memoryService = mock(MemoryService.class);
        ToolRegistry toolRegistry = mock(ToolRegistry.class);
        LlmClient llmClient = mock(LlmClient.class);

        when(memoryService.loadPreference(1L)).thenReturn(PlayerPreference.builder().build());

        RagHit hit = RagHit.builder()
                .guideId(202L)
                .title("黄泉抽取建议")
                .version("2.1")
                .snippet("建议搭配虚无队友。")
                .url("/guides/202")
                .build();

        when(toolRegistry.invoke(eq("search_guides"), any()))
                .thenReturn(ToolResult.ok(List.of(hit), 10));
        when(toolRegistry.invoke(eq("check_compatibility"), any()))
                .thenReturn(ToolResult.ok(List.of(), 5));

        // 模拟 LLM 抛出异常
        when(llmClient.chat(any(), any())).thenThrow(new RuntimeException("API Timeout"));

        AgentService agentService = new AgentService(memoryService, toolRegistry, llmClient);

        ChatRequest req = new ChatRequest();
        req.setMessage("黄泉值得抽吗？");

        ChatResponse resp = agentService.chat(1L, req);

        // 验证降级为模板汇总，系统未发生未捕获异常
        assertThat(resp.getAnswer()).contains("黄泉抽取建议");
        assertThat(resp.getPlan()).hasSize(3);
        assertThat(resp.getPlan().get(2).getStatus()).isEqualTo("DEGRADED");
    }
}
