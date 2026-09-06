package com.gametips.platform.module.tool.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.module.tool.dto.ToolDefinition;
import com.gametips.platform.module.tool.registry.ToolRegistry;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * Tool 元数据查询(V2 architecture §5.2:供前端调试面板用)。
 */
@RestController
@RequestMapping("/api/v1/agent/tools")
@RequiredArgsConstructor
public class ToolMetaController {

    private final ToolRegistry registry;

    @GetMapping
    public ApiResponse<List<ToolDefinition>> list() {
        return ApiResponse.ok(registry.list());
    }
}
