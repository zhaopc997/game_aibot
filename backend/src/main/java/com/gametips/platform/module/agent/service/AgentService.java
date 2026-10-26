package com.gametips.platform.module.agent.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gametips.platform.common.trace.TraceContext;
import com.gametips.platform.module.agent.dto.ChatRequest;
import com.gametips.platform.module.agent.dto.ChatResponse;
import com.gametips.platform.module.ai.service.llm.LlmClient;
import com.gametips.platform.module.ai.service.llm.LlmResponse;
import com.gametips.platform.module.ai.service.llm.LlmToolCall;
import com.gametips.platform.module.memory.dto.ConversationMessage;
import com.gametips.platform.module.memory.dto.PlayerPreference;
import com.gametips.platform.module.memory.service.MemoryService;
import com.gametips.platform.module.rag.dto.RagHit;
import com.gametips.platform.module.tool.dto.ToolResult;
import com.gametips.platform.module.tool.registry.ToolRegistry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.function.Consumer;

/**
 * Agent 编排门面。
 * 支持两套执行路径：
 * 1. 真实 LLM 且支持 Tools 时，走自主决策的 ReAct 循环（动态调用 search_guides, simulate_build, get_game_map, get_wiki_entry 等）。
 * 2. MockLlmClient 或降级阶段时，平滑回退到稳定的预设两步流水线（search_guides -> check_compatibility -> synthesize）。
 * 同时支持同步阻塞与 SSE 流式输出（SseEmitter）。
 */
@Slf4j
@Service
public class AgentService {

    private static final int MAX_REACT_STEPS = 4;
    private static final int MAX_HISTORY_MESSAGES = 12;

    private final MemoryService memoryService;
    private final ToolRegistry toolRegistry;
    private final LlmClient llmClient;
    private final ObjectMapper objectMapper;

    public AgentService(MemoryService memoryService, ToolRegistry toolRegistry, LlmClient llmClient) {
        this(memoryService, toolRegistry, llmClient, new ObjectMapper());
    }

    @org.springframework.beans.factory.annotation.Autowired
    public AgentService(MemoryService memoryService, ToolRegistry toolRegistry, LlmClient llmClient, ObjectMapper objectMapper) {
        this.memoryService = memoryService;
        this.toolRegistry = toolRegistry;
        this.llmClient = llmClient;
        this.objectMapper = objectMapper != null ? objectMapper : new ObjectMapper();
    }

    /**
     * 同步问答入口
     */
    public ChatResponse chat(Long userId, ChatRequest req) {
        return chatInternal(userId, req, null, null);
    }

    /**
     * SSE 流式问答入口
     */
    public SseEmitter chatStream(Long userId, ChatRequest req) {
        SseEmitter emitter = new SseEmitter(60_000L);
        CompletableFuture.runAsync(() -> {
            try {
                ChatResponse resp = chatInternal(userId, req, step -> {
                    try {
                        emitter.send(SseEmitter.event().name("step").data(step));
                    } catch (Exception e) {
                        log.warn("[agent-sse] send step error: {}", e.getMessage());
                    }
                }, delta -> {
                    try {
                        emitter.send(SseEmitter.event().name("delta").data(Map.of("text", delta)));
                    } catch (Exception e) {
                        log.warn("[agent-sse] send delta error: {}", e.getMessage());
                    }
                });
                emitter.send(SseEmitter.event().name("complete").data(resp));
                emitter.complete();
            } catch (Exception e) {
                log.error("[agent-sse] execution error: {}", e.getMessage(), e);
                try {
                    emitter.send(SseEmitter.event().name("error").data(Map.of("message", e.getMessage() == null ? "未知异常" : e.getMessage())));
                } catch (Exception ignore) {}
                emitter.completeWithError(e);
            }
        });
        return emitter;
    }

    /**
     * 内部核心执行编排
     */
    private ChatResponse chatInternal(
            Long userId,
            ChatRequest req,
            Consumer<ChatResponse.PlanStep> onStep,
            Consumer<String> onDelta) {

        UUID convId = req.getConversationId() != null
                ? req.getConversationId()
                : UUID.randomUUID();
        log.info("[agent] chat start user={} conv={} traceId={} msg='{}'",
                userId, convId, TraceContext.currentTraceId(), req.getMessage());

        // 1. 写短期记忆(USER)
        memoryService.shortTerm(convId, ConversationMessage.builder()
                .messageId(UUID.randomUUID())
                .conversationId(convId)
                .role(ConversationMessage.Role.USER)
                .content(req.getMessage())
                .createdAt(java.time.Instant.now())
                .build());

        // 1.5 读回历史消息(排除本轮刚写入的这条)
        List<ConversationMessage> history = readHistory(convId);

        // 2. 读玩家长期偏好
        PlayerPreference pref = memoryService.loadPreference(userId);
        log.debug("[agent] pref loaded user={} style={}", userId, pref != null ? pref.getPlayStyle() : "none");

        // 3. 判断是否启用自主 ReAct 工具调用
        if (llmClient != null && llmClient.supportsTools()) {
            try {
                return runReAct(userId, req, convId, history, pref, onStep, onDelta);
            } catch (Exception ex) {
                log.warn("[agent] ReAct loop failed, fallback to pipeline: {}", ex.getMessage());
            }
        }

        // 4. 默认/降级流水线
        return runPipelineFallback(userId, req, convId, history, pref, onStep, onDelta);
    }

    /**
     * 动态 ReAct 循环执行模式
     */
    private ChatResponse runReAct(
            Long userId,
            ChatRequest req,
            UUID convId,
            List<ConversationMessage> history,
            PlayerPreference pref,
            Consumer<ChatResponse.PlanStep> onStep,
            Consumer<String> onDelta) {

        List<ChatResponse.PlanStep> steps = new ArrayList<>();
        List<ChatResponse.SourceRef> sources = new ArrayList<>();

        String systemPrompt = """
                你是一名专业的游戏智能助手。你有以下能力：
                1. 可以调用 search_guides 检索攻略库中的高质量攻略片段；
                2. 可以调用 simulate_build 模拟角色属性与装备配装（支持原神、崩铁等）；
                3. 可以调用 get_game_map 查询互动地图传送点、宝箱点位；
                4. 可以调用 get_wiki_entry 查询游戏百科词条背景设定；
                5. 可以调用 check_compatibility 检查攻略的版本有效性与过期风险。
                请根据玩家问题自主决定是否需要调用工具。可单次或分步连续调用工具，若信息充分亦可直接作答。
                最终回答应当条理清晰、言简意赅，带版本号与依据。
                玩家偏好: %s
                当前时间: %s
                """.formatted(
                pref != null && pref.getPlayStyle() != null ? pref.getPlayStyle() : "常规风格",
                java.time.LocalDate.now()
        );

        List<Map<String, Object>> messages = new ArrayList<>();
        messages.add(Map.of("role", "system", "content", systemPrompt));

        if (!history.isEmpty()) {
            for (ConversationMessage m : history) {
                String role = m.getRole() == ConversationMessage.Role.USER ? "user" : "assistant";
                String content = m.getContent() == null ? "" : m.getContent().trim();
                if (!content.isEmpty()) {
                    messages.add(Map.of("role", role, "content", content));
                }
            }
        }
        messages.add(Map.of("role", "user", "content", req.getMessage()));

        List<Map<String, Object>> tools = toolRegistry.toOpenAiTools();
        String finalAnswer = null;

        for (int iter = 1; iter <= MAX_REACT_STEPS; iter++) {
            LlmResponse resp = llmClient.chatWithTools(messages, tools);
            if (!resp.hasToolCalls()) {
                finalAnswer = resp.getContent();
                break;
            }

            // 模型发出工具调用指令
            Map<String, Object> assistantMsg = new java.util.LinkedHashMap<>();
            assistantMsg.put("role", "assistant");
            if (resp.getContent() != null) {
                assistantMsg.put("content", resp.getContent());
            }
            List<Map<String, Object>> callList = new ArrayList<>();
            for (LlmToolCall tc : resp.getToolCalls()) {
                callList.add(Map.of(
                        "id", tc.getId() != null ? tc.getId() : ("call_" + UUID.randomUUID().toString().substring(0, 8)),
                        "type", "function",
                        "function", Map.of(
                                "name", tc.getName(),
                                "arguments", toJson(tc.getArguments())
                        )
                ));
            }
            assistantMsg.put("tool_calls", callList);
            messages.add(assistantMsg);

            // 逐个执行工具调用
            for (LlmToolCall tc : resp.getToolCalls()) {
                long t0 = System.currentTimeMillis();
                ToolResult tr = toolRegistry.invoke(tc.getName(), tc.getArguments());
                long dur = System.currentTimeMillis() - t0;

                ChatResponse.PlanStep step = ChatResponse.PlanStep.builder()
                        .stepId(steps.size() + 1)
                        .tool(tc.getName())
                        .status(tr.isSuccess() ? "SUCCESS" : "FAILED")
                        .durationMs(dur)
                        .summary(summarizeToolResult(tc.getName(), tr))
                        .build();
                steps.add(step);
                if (onStep != null) {
                    onStep.accept(step);
                }

                if ("search_guides".equals(tc.getName()) && tr.isSuccess() && tr.getOutput() instanceof List<?> list) {
                    for (Object o : list) {
                        if (o instanceof RagHit h) {
                            sources.add(ChatResponse.SourceRef.builder()
                                    .guideId(h.getGuideId())
                                    .title(h.getTitle())
                                    .version(h.getVersion())
                                    .url(h.getUrl())
                                    .build());
                        }
                    }
                }

                Map<String, Object> toolMsg = new java.util.LinkedHashMap<>();
                toolMsg.put("role", "tool");
                toolMsg.put("tool_call_id", tc.getId() != null ? tc.getId() : "");
                toolMsg.put("content", tr.isSuccess() ? toJson(tr.getOutput()) : "{\"error\":\"" + tr.getError() + "\"}");
                messages.add(toolMsg);
            }
        }

        if (finalAnswer == null || finalAnswer.isBlank()) {
            finalAnswer = "（AI 分析完成）根据工具检索与数值模拟，已整理出上述执行步骤与结果。";
        }

        // 流式推送 delta
        emitDeltaChunks(finalAnswer, onDelta);

        // 写短期记忆(ASSISTANT)
        memoryService.shortTerm(convId, ConversationMessage.builder()
                .messageId(UUID.randomUUID())
                .conversationId(convId)
                .role(ConversationMessage.Role.ASSISTANT)
                .content(finalAnswer)
                .createdAt(java.time.Instant.now())
                .build());

        return ChatResponse.builder()
                .conversationId(convId)
                .messageId(UUID.randomUUID())
                .answer(finalAnswer)
                .plan(steps)
                .sources(sources)
                .degraded(false)
                .meta(Map.of(
                        "trace_id", TraceContext.currentTraceId(),
                        "react_enabled", true,
                        "llm_synthesized", true,
                        "steps_count", steps.size()
                ))
                .build();
    }

    /**
     * 预设流水线执行模式（兼作为 Mock / 单测 / 异常降级模式）
     */
    private ChatResponse runPipelineFallback(
            Long userId,
            ChatRequest req,
            UUID convId,
            List<ConversationMessage> history,
            PlayerPreference pref,
            Consumer<ChatResponse.PlanStep> onStep,
            Consumer<String> onDelta) {

        List<ChatResponse.PlanStep> steps = new ArrayList<>();
        List<RagHit> hits;
        List<ChatResponse.SourceRef> sources;

        // step 1: search_guides
        long t0 = System.currentTimeMillis();
        ToolResult s1 = toolRegistry.invoke("search_guides", Map.of(
                "query", req.getMessage()
        ));
        long d1 = System.currentTimeMillis() - t0;
        if (!s1.isSuccess() || !(s1.getOutput() instanceof List<?> raw)) {
            ChatResponse.PlanStep fStep = stepFail(1, "search_guides", d1, s1.getError());
            steps.add(fStep);
            if (onStep != null) onStep.accept(fStep);
            return errorResponse(convId, "检索失败", steps);
        }
        hits = raw.stream().filter(o -> o instanceof RagHit).map(o -> (RagHit) o).toList();
        ChatResponse.PlanStep step1 = ChatResponse.PlanStep.builder()
                .stepId(1).tool("search_guides").status("SUCCESS")
                .durationMs(d1).summary("召回 " + hits.size() + " 条攻略片段")
                .build();
        steps.add(step1);
        if (onStep != null) onStep.accept(step1);

        // step 2: check_compatibility
        List<Long> guideIds = hits.stream().map(RagHit::getGuideId).toList();
        long t1 = System.currentTimeMillis();
        ToolResult s2;
        if (guideIds.isEmpty()) {
            s2 = ToolResult.ok(List.of(), 0);
        } else {
            Map<String, Object> args = new HashMap<>();
            args.put("guide_ids", guideIds);
            s2 = toolRegistry.invoke("check_compatibility", args);
        }
        long d2 = System.currentTimeMillis() - t1;
        List<String> riskNotes = collectRiskNotes(s2);
        ChatResponse.PlanStep step2 = ChatResponse.PlanStep.builder()
                .stepId(2).tool("check_compatibility")
                .status(s2.isSuccess() ? "SUCCESS" : "FAILED")
                .durationMs(d2)
                .summary(s2.isSuccess()
                        ? (riskNotes.isEmpty() ? "兼容性检查完成,无风险项"
                        : "兼容性检查完成,发现 " + riskNotes.size() + " 条风险")
                        : ("失败: " + s2.getError()))
                .build();
        steps.add(step2);
        if (onStep != null) onStep.accept(step2);

        // 4. 拼装参考来源
        sources = hits.stream().map(h -> ChatResponse.SourceRef.builder()
                .guideId(h.getGuideId())
                .title(h.getTitle())
                .version(h.getVersion())
                .url(h.getUrl())
                .build()).toList();

        // 5. 调用 LLM 进行综合回答 (Synthesize Step)
        long t2 = System.currentTimeMillis();
        String answer;
        boolean llmSynthesized = false;

        StringBuilder contextSb = new StringBuilder();

        if (!history.isEmpty()) {
            contextSb.append("【历史对话】\n");
            for (ConversationMessage m : history) {
                String role = m.getRole() == ConversationMessage.Role.USER ? "用户" : "助手";
                String content = m.getContent() == null ? "" : m.getContent().trim();
                if (content.isEmpty()) continue;
                contextSb.append(role).append(": ")
                        .append(content.length() > 500 ? content.substring(0, 500) + "…" : content)
                        .append('\n');
            }
            contextSb.append('\n');
        }

        if (pref != null && pref.getPlayStyle() != null) {
            contextSb.append("【玩家偏好】偏好风格: ").append(pref.getPlayStyle()).append("\n");
        }
        if (!riskNotes.isEmpty()) {
            contextSb.append("【重要提醒】以下参考攻略存在版本或状态问题，回答时必须显式提示用户核实：\n");
            for (String n : riskNotes) {
                contextSb.append("- ").append(n).append('\n');
            }
            contextSb.append('\n');
        }
        for (RagHit h : hits) {
            contextSb.append("【").append(h.getTitle()).append("】(版本: ").append(h.getVersion()).append(")\n")
                    .append(h.getSnippet()).append("\n\n");
        }

        try {
            if (llmClient != null && (!hits.isEmpty() || !contextSb.isEmpty())) {
                answer = llmClient.chat(req.getMessage(), contextSb.toString());
                llmSynthesized = (answer != null && !answer.isBlank());
            } else {
                answer = buildTemplateAnswer(req.getMessage(), hits, sources);
            }
        } catch (Exception e) {
            log.warn("[agent] llm synthesize error, fallback to template: {}", e.getMessage());
            answer = buildTemplateAnswer(req.getMessage(), hits, sources);
        }

        long d3 = System.currentTimeMillis() - t2;
        ChatResponse.PlanStep step3 = ChatResponse.PlanStep.builder()
                .stepId(3).tool("llm_synthesize")
                .status(llmSynthesized ? "SUCCESS" : "DEGRADED")
                .durationMs(d3)
                .summary(llmSynthesized ? "LLM 综合答复生成完毕" : "LLM 降级为模板汇总")
                .build();
        steps.add(step3);
        if (onStep != null) onStep.accept(step3);

        // 流式推送
        emitDeltaChunks(answer, onDelta);

        // 6. 写短期记忆(ASSISTANT)
        memoryService.shortTerm(convId, ConversationMessage.builder()
                .messageId(UUID.randomUUID())
                .conversationId(convId)
                .role(ConversationMessage.Role.ASSISTANT)
                .content(answer)
                .createdAt(java.time.Instant.now())
                .build());

        return ChatResponse.builder()
                .conversationId(convId)
                .messageId(UUID.randomUUID())
                .answer(answer)
                .plan(steps)
                .sources(sources)
                .degraded(!llmSynthesized && hits.isEmpty())
                .meta(Map.of(
                        "trace_id", TraceContext.currentTraceId(),
                        "llm_synthesized", llmSynthesized,
                        "pref_loaded", pref != null
                ))
                .build();
    }

    private String summarizeToolResult(String tool, ToolResult tr) {
        if (!tr.isSuccess()) {
            return "执行失败: " + tr.getError();
        }
        if ("search_guides".equals(tool) && tr.getOutput() instanceof List<?> l) {
            return "召回 " + l.size() + " 条攻略片段";
        }
        if ("check_compatibility".equals(tool)) {
            List<String> risks = collectRiskNotes(tr);
            return risks.isEmpty() ? "兼容性检查完成,无风险项" : "发现 " + risks.size() + " 项版本风险";
        }
        if ("simulate_build".equals(tool)) {
            return "模拟配装属性与收益计算完成";
        }
        if ("get_game_map".equals(tool)) {
            return "地图传送与标记点位查询完成";
        }
        if ("get_wiki_entry".equals(tool)) {
            return "游戏百科词条信息已加载";
        }
        return "执行成功";
    }

    private void emitDeltaChunks(String text, Consumer<String> onDelta) {
        if (onDelta == null || text == null || text.isEmpty()) return;
        int len = text.length();
        int chunkSize = 6;
        for (int i = 0; i < len; i += chunkSize) {
            String chunk = text.substring(i, Math.min(len, i + chunkSize));
            onDelta.accept(chunk);
            try {
                Thread.sleep(15);
            } catch (InterruptedException ignore) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private String toJson(Object obj) {
        if (obj == null) return "{}";
        try {
            return objectMapper.writeValueAsString(obj);
        } catch (Exception e) {
            return String.valueOf(obj);
        }
    }

    @SuppressWarnings("unchecked")
    private List<String> collectRiskNotes(ToolResult result) {
        List<String> notes = new ArrayList<>();
        if (!result.isSuccess() || !(result.getOutput() instanceof List<?> rows)) {
            return notes;
        }
        for (Object row : rows) {
            if (!(row instanceof Map<?, ?> map)) continue;
            Object status = map.get("status");
            String st = status == null ? "UNKNOWN" : status.toString();
            if ("COMPATIBLE".equals(st)) continue;
            Object note = map.get("note");
            Object title = map.get("title");
            notes.add("攻略[" + (title != null ? title : map.get("guide_id")) + "] " + st
                    + (note != null ? "：" + note : ""));
        }
        return notes;
    }

    private List<ConversationMessage> readHistory(UUID convId) {
        List<ConversationMessage> all;
        try {
            all = memoryService.readShort(convId);
        } catch (Exception e) {
            log.warn("[agent] readShort failed conv={}: {}", convId, e.getMessage());
            return List.of();
        }
        if (all == null || all.isEmpty()) {
            return List.of();
        }
        int end = all.size() - 1;
        if (end <= 0) return List.of();
        int start = Math.max(0, end - MAX_HISTORY_MESSAGES);
        return List.copyOf(all.subList(start, end));
    }

    private String buildTemplateAnswer(String question, List<RagHit> hits, List<ChatResponse.SourceRef> sources) {
        if (hits.isEmpty()) {
            return "未找到相关攻略。请换个问题或指定游戏。";
        }
        StringBuilder sb = new StringBuilder();
        sb.append("针对你的问题「").append(question).append("」,找到以下参考:\n\n");
        for (int i = 0; i < sources.size(); i++) {
            ChatResponse.SourceRef s = sources.get(i);
            sb.append(i + 1).append(". ").append(s.getTitle())
                    .append(" (版本 ").append(s.getVersion()).append(")\n");
        }
        sb.append("\n[说明] 当前为基础流水线模式，配置大模型后可开启自主 ReAct 推理与深度汇总。");
        return sb.toString();
    }

    private ChatResponse.PlanStep stepFail(int id, String tool, long dur, String err) {
        return ChatResponse.PlanStep.builder()
                .stepId(id).tool(tool).status("FAILED")
                .durationMs(dur).summary(err == null ? "unknown" : err)
                .build();
    }

    private ChatResponse errorResponse(UUID convId, String msg, List<ChatResponse.PlanStep> steps) {
        return ChatResponse.builder()
                .conversationId(convId)
                .messageId(UUID.randomUUID())
                .answer(msg)
                .plan(steps)
                .sources(List.of())
                .degraded(true)
                .meta(Map.of("trace_id", TraceContext.currentTraceId(), "mock", true))
                .build();
    }
}
