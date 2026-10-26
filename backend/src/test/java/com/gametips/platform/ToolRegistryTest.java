package com.gametips.platform;

import com.gametips.platform.module.tool.builtin.SystemTools;
import com.gametips.platform.module.tool.dto.ToolDefinition;
import com.gametips.platform.module.tool.dto.ToolResult;
import com.gametips.platform.module.tool.registry.ToolRegistry;
import org.junit.jupiter.api.Test;
import org.springframework.context.ApplicationContext;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class ToolRegistryTest {

    @Test
    void shouldScanAndInvokeSystemToolsWithCastConversion() {
        ApplicationContext ctx = mock(ApplicationContext.class);
        when(ctx.getBeanDefinitionNames()).thenReturn(new String[]{"systemTools"});
        SystemTools systemTools = new SystemTools();
        when(ctx.getBean("systemTools")).thenReturn(systemTools);

        ToolRegistry registry = new ToolRegistry(ctx);
        registry.scan();

        List<ToolDefinition> tools = registry.list();
        assertThat(tools).extracting(ToolDefinition::getName)
                .contains("get_game_map", "simulate_build", "get_wiki_entry");

        // 测试类型自适应转换（将 String 形式的 "90" 转换为 Integer targetLevel）
        ToolResult res = registry.invoke("simulate_build", Map.of(
                "character", "钟离",
                "target_level", "90",
                "weapon", "贯虹之槊"
        ));

        assertThat(res.isSuccess()).isTrue();
        assertThat(res.getOutput()).isInstanceOf(Map.class);
        @SuppressWarnings("unchecked")
        Map<String, Object> output = (Map<String, Object>) res.getOutput();
        assertThat(output.get("character")).isEqualTo("钟离");
        assertThat(output.get("level")).isEqualTo(90);

        // 测试地图工具调用
        ToolResult mapRes = registry.invoke("get_game_map", Map.of(
                "game_id", "yuanshen",
                "region", "璃月港"
        ));
        assertThat(mapRes.isSuccess()).isTrue();
        assertThat(mapRes.getOutput()).isInstanceOf(List.class);

        // 测试百科词条工具调用
        ToolResult wikiRes = registry.invoke("get_wiki_entry", Map.of(
                "keyword", "绝缘之旗印"
        ));
        assertThat(wikiRes.isSuccess()).isTrue();
        assertThat(wikiRes.getOutput()).isInstanceOf(Map.class);
    }
}
