package com.gametips.platform.module.agent.service;

import com.gametips.platform.common.trace.TraceContext;
import com.gametips.platform.module.agent.dto.ChatRequest;
import com.gametips.platform.module.agent.dto.ChatResponse;
import com.gametips.platform.module.memory.dto.ConversationMessage;
import com.gametips.platform.module.memory.dto.PlayerPreference;
import com.gametips.platform.module.memory.service.MemoryService;
import com.gametips.platform.module.rag.dto.RagHit;
import com.gametips.platform.module.tool.dto.ToolResult;
import com.gametips.platform.module.tool.registry.ToolRegistry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Agent 编排门面(§4.2 plan-and-execute 的骨架实现)。
 *
 * <p>骨架阶段:不接真 LLM,固定跑两步:
 *   step1: search_guides(query=userMsg)
 *   step2: check_compatibility(guide_ids=step1 的 ids, version=latest)
 *   step3: 模板拼装 answer
 *
 * <p>接 LangChain4j 后替换为:
 *   Planner LLM 一次性生成 plan JSON → Executor 按序执行 → Reflect 决定继续/重试/完成
 *
 * <p>本类的责任:Plan/Step 调度、Tool 调用、Memory 串联、TraceId 串联。
 */
@Slf4j
@Service
public class AgentService {

    private final MemoryService memoryService;
    private final ToolRegistry toolRegistry;

    public AgentService(MemoryService memoryService, ToolRegistry toolRegistry) {
        this.memoryService = memoryService;
        this.toolRegistry = toolRegistry;
    }

    public ChatResponse chat(Long userId, ChatRequest req) {
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

        // 2. 读玩家长期偏好(注入 system prompt;骨架阶段只读取)
        PlayerPreference pref = memoryService.loadPreference(userId);
        log.debug("[agent] pref loaded user={} style={}", userId, pref.getPlayStyle());

        // 3. 执行 plan(骨架:固定 2 步)
        List<ChatResponse.PlanStep> steps = new ArrayList<>();
        List<RagHit> hits;
        List<ChatResponse.SourceRef> sources;

        // step 1: search_guides
        long t0 = System.currentTimeMillis();
        ToolResult s1 = toolRegistry.invoke("search_guides", Map.of(
                "query", req.getMessage()
                // game_id / version_id 缺省,真实阶段从 Planner LLM 决策注入
        ));
        long d1 = System.currentTimeMillis() - t0;
        if (!s1.isSuccess() || !(s1.getOutput() instanceof List<?> raw)) {
            steps.add(stepFail(1, "search_guides", d1, s1.getError()));
            return errorResponse(convId, "检索失败", steps);
        }
        hits = raw.stream().filter(o -> o instanceof RagHit).map(o -> (RagHit) o).toList();
        steps.add(ChatResponse.PlanStep.builder()
                .stepId(1).tool("search_guides").status("SUCCESS")
                .durationMs(d1).summary("召回 " + hits.size() + " 条攻略片段")
                .build());

        // step 2: check_compatibility
        List<Long> guideIds = hits.stream().map(RagHit::getGuideId).toList();
        long t1 = System.currentTimeMillis();
        ToolResult s2;
        if (guideIds.isEmpty()) {
            s2 = ToolResult.ok(List.of(), 0);
        } else {
            Map<String, Object> args = new HashMap<>();
            args.put("guide_ids", guideIds);
            args.put("version_id", "latest");
            s2 = toolRegistry.invoke("check_compatibility", args);
        }
        long d2 = System.currentTimeMillis() - t1;
        steps.add(ChatResponse.PlanStep.builder()
                .stepId(2).tool("check_compatibility")
                .status(s2.isSuccess() ? "SUCCESS" : "FAILED")
                .durationMs(d2)
                .summary(s2.isSuccess() ? "兼容性检查完成" : ("失败: " + s2.getError()))
                .build());

        // 4. 拼装 answer(骨架:模板;真实阶段:Synthesize Step 由 LLM 生成)
        sources = hits.stream().map(h -> ChatResponse.SourceRef.builder()
                .guideId(h.getGuideId())
                .title(h.getTitle())
                .version(h.getVersion())
                .url(h.getUrl())
                .build()).toList();

        String answer = buildTemplateAnswer(req.getMessage(), hits, sources);

        // 5. 写短期记忆(ASSISTANT)
        memoryService.shortTerm(convId, ConversationMessage.builder()
                .messageId(UUID.randomUUID())
                .conversationId(convId)
                .role(ConversationMessage.Role.ASSISTANT)
                .content(answer)
                .createdAt(java.time.Instant.now())
                .build());

        ChatResponse resp = ChatResponse.builder()
                .conversationId(convId)
                .messageId(UUID.randomUUID())
                .answer(answer)
                .plan(steps)
                .sources(sources)
                .degraded(false)
                .meta(Map.of(
                        "trace_id", TraceContext.currentTraceId(),
                        "mock", true,
                        "pref_loaded", pref != null
                ))
                .build();
        log.info("[agent] chat done conv={} steps={} sources={}",
                convId, steps.size(), sources.size());
        return resp;
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
        sb.append("\n[骨架阶段]这是模板拼装的答案,接 LLM 后会替换为 Synthesize 步骤生成的更自然回答。");
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
