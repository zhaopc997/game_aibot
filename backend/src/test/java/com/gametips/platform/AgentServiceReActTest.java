package com.gametips.platform;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gametips.platform.module.agent.dto.ChatRequest;
import com.gametips.platform.module.agent.dto.ChatResponse;
import com.gametips.platform.module.agent.service.AgentService;
import com.gametips.platform.module.ai.service.llm.LlmClient;
import com.gametips.platform.module.ai.service.llm.LlmResponse;
import com.gametips.platform.module.ai.service.llm.LlmToolCall;
import com.gametips.platform.module.memory.dto.PlayerPreference;
import com.gametips.platform.module.memory.service.MemoryService;
import com.gametips.platform.module.rag.dto.RagHit;
import com.gametips.platform.module.tool.dto.ToolResult;
import com.gametips.platform.module.tool.registry.ToolRegistry;
import org.junit.jupiter.api.Test;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class AgentServiceReActTest {

    @Test
    void chat_shouldExecuteDynamicReActLoopWithTools() {
        MemoryService memoryService = mock(MemoryService.class);
        ToolRegistry toolRegistry = mock(ToolRegistry.class);
        LlmClient llmClient = mock(LlmClient.class);

        when(memoryService.loadPreference(1L)).thenReturn(
                PlayerPreference.builder().playStyle("硬核数值 / 追求毕业").build()
        );
        when(llmClient.supportsTools()).thenReturn(true);
        when(toolRegistry.toOpenAiTools()).thenReturn(List.of(
                Map.of("type", "function", "function", Map.of("name", "simulate_build"))
        ));

        // 第 1 轮：模型决定调用 simulate_build 工具
        LlmToolCall toolCall = LlmToolCall.builder()
                .id("call_sim_1")
                .name("simulate_build")
                .arguments(Map.of("character", "钟离", "weapon", "贯虹之槊"))
                .build();
        LlmResponse turn1 = LlmResponse.builder()
                .content(null)
                .toolCalls(List.of(toolCall))
                .build();

        // 第 2 轮：模型拿到工具结果后，输出最终分析回答
        LlmResponse turn2 = LlmResponse.builder()
                .content("（AI 分析）模拟计算得出：钟离佩戴贯虹之槊时生命值 45000，盾量极厚，输出与护盾达到平衡。")
                .toolCalls(List.of())
                .build();

        when(llmClient.chatWithTools(any(), any()))
                .thenReturn(turn1)
                .thenReturn(turn2);

        when(toolRegistry.invoke(eq("simulate_build"), any()))
                .thenReturn(ToolResult.ok(Map.of("hp", 45000, "shieldStrength", 14200), 15));

        AgentService agentService = new AgentService(memoryService, toolRegistry, llmClient, new ObjectMapper());

        ChatRequest req = new ChatRequest();
        req.setMessage("钟离带贯虹之槊盾量够用吗？帮我模拟一下");

        ChatResponse resp = agentService.chat(1L, req);

        assertThat(resp).isNotNull();
        assertThat(resp.getAnswer()).contains("45000");
        assertThat(resp.getPlan()).hasSize(1);
        assertThat(resp.getPlan().get(0).getTool()).isEqualTo("simulate_build");
        assertThat(resp.getPlan().get(0).getStatus()).isEqualTo("SUCCESS");
        assertThat(resp.getMeta().get("react_enabled")).isEqualTo(true);
    }

    @Test
    void chat_shouldFallbackToPipelineIfReActThrowsException() {
        MemoryService memoryService = mock(MemoryService.class);
        ToolRegistry toolRegistry = mock(ToolRegistry.class);
        LlmClient llmClient = mock(LlmClient.class);

        when(memoryService.loadPreference(1L)).thenReturn(PlayerPreference.builder().build());
        when(llmClient.supportsTools()).thenReturn(true);
        // 模拟 ReAct 第一次调用 LLM 发生网络中断
        when(llmClient.chatWithTools(any(), any())).thenThrow(new RuntimeException("LLM network disconnected"));

        RagHit hit = RagHit.builder()
                .guideId(101L)
                .title("钟离毕业攻略")
                .version("4.2")
                .snippet("主词条选择生生生")
                .url("/guides/101")
                .build();
        when(toolRegistry.invoke(eq("search_guides"), any())).thenReturn(ToolResult.ok(List.of(hit), 10));
        when(toolRegistry.invoke(eq("check_compatibility"), any())).thenReturn(ToolResult.ok(List.of(), 5));
        when(llmClient.chat(any(), any())).thenReturn("（降级答复）根据攻略 101，主词条选择生生生。");

        AgentService agentService = new AgentService(memoryService, toolRegistry, llmClient, new ObjectMapper());

        ChatRequest req = new ChatRequest();
        req.setMessage("钟离配装");

        ChatResponse resp = agentService.chat(1L, req);

        assertThat(resp).isNotNull();
        assertThat(resp.getAnswer()).contains("生生生");
        assertThat(resp.getPlan()).hasSize(3); // 降级回退到 pipeline 模式
    }

    @Test
    void chatStream_shouldReturnEmitter() {
        MemoryService memoryService = mock(MemoryService.class);
        ToolRegistry toolRegistry = mock(ToolRegistry.class);
        LlmClient llmClient = mock(LlmClient.class);

        when(memoryService.loadPreference(1L)).thenReturn(PlayerPreference.builder().build());
        when(toolRegistry.invoke(eq("search_guides"), any())).thenReturn(ToolResult.ok(List.of(), 10));
        when(toolRegistry.invoke(eq("check_compatibility"), any())).thenReturn(ToolResult.ok(List.of(), 5));

        AgentService agentService = new AgentService(memoryService, toolRegistry, llmClient, new ObjectMapper());

        ChatRequest req = new ChatRequest();
        req.setMessage("测试流式接口");

        SseEmitter emitter = agentService.chatStream(1L, req);
        assertThat(emitter).isNotNull();
    }
}
