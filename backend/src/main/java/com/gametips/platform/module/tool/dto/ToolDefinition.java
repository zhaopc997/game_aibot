package com.gametips.platform.module.tool.dto;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.gametips.platform.module.tool.annotation.RiskLevel;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.lang.reflect.Method;
import java.util.List;

/**
 * Tool 元数据(已注册到 Registry 的工具)。
 *
 * <p>骨架阶段:包含反射 Method + 注解信息,真实调用时按 method.invoke(bean, args) 执行;
 * 接 LangChain4j 后会多出 {@code ToolSpecification} 字段。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ToolDefinition {

    /** Tool 名(给 LLM 看的 function name) */
    private String name;

    /** 描述(给 LLM 看) */
    private String description;

    /** 风险等级 */
    private RiskLevel riskLevel;

    /** 参数 schema 描述(给人看的;真实 LLM 调用走 LangChain4j) */
    private List<ParamSpec> params;

    /** 反射 Method,真正调用时用;骨架阶段保留便于手动测试 */
    @JsonIgnore
    @Builder.Default
    private transient Method method = null;

    /** 持有该 Method 的 Bean 实例;骨架阶段保留便于手动测试 */
    @JsonIgnore
    @Builder.Default
    private transient Object bean = null;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ParamSpec {
        private String name;
        private String type;
        private String description;
        private boolean required;
    }
}
