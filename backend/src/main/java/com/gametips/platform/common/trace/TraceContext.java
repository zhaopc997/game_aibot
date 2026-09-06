package com.gametips.platform.common.trace;

import org.slf4j.MDC;

import java.util.UUID;

/**
 * 调用链追踪上下文。
 *
 * <p>每个 HTTP 请求进入时由 {@link TraceIdFilter} 生成 traceId 并写入 SLF4J MDC;
 * Agent / RAG / Tool 内部日志会自动带上该 ID,便于跨模块排查一次完整 Agent 会话。
 *
 * <p>用法:
 * <pre>{@code
 *   log.info("step done");        // 日志自动含 traceId
 *   String current = TraceContext.currentTraceId();
 * }</pre>
 */
public final class TraceContext {

    /** SLF4J MDC key,与 logback pattern %X{traceId} 配合 */
    public static final String MDC_KEY = "traceId";

    private TraceContext() {}

    /** 当前请求的 traceId;无请求上下文时返回 "no-trace"。 */
    public static String currentTraceId() {
        String v = MDC.get(MDC_KEY);
        return v == null || v.isEmpty() ? "no-trace" : v;
    }

    /** 生成新的 traceId 并写入 MDC;由 TraceIdFilter 在请求入口调用。 */
    public static String init() {
        String id = UUID.randomUUID().toString().replace("-", "").substring(0, 16);
        MDC.put(MDC_KEY, id);
        return id;
    }

    /** 清理 MDC;由 TraceIdFilter 在 finally 块调用。 */
    public static void clear() {
        MDC.remove(MDC_KEY);
    }
}
