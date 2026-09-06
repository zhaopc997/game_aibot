package com.gametips.platform.module.tool.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Tool 一次调用的结果(给 LLM 看)。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ToolResult {

    /** 是否成功 */
    private boolean success;

    /** 输出内容(任意 JSON 可序列化的对象) */
    private Object output;

    /** 失败时的错误信息(成功时为空) */
    private String error;

    /** 工具元数据:调用耗时 ms、入参摘要(便于审计) */
    private Map<String, Object> meta;

    public static ToolResult ok(Object output, long durationMs) {
        return ToolResult.builder()
                .success(true)
                .output(output)
                .meta(Map.of("duration_ms", durationMs))
                .build();
    }

    public static ToolResult fail(String error, long durationMs) {
        return ToolResult.builder()
                .success(false)
                .error(error)
                .meta(Map.of("duration_ms", durationMs))
                .build();
    }
}
