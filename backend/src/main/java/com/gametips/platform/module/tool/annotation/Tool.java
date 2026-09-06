package com.gametips.platform.module.tool.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 标记一个方法为 Agent 可调用的 Tool(V2 architecture §4.3)。
 *
 * <p>被该注解标注的 Spring Bean 方法会在应用启动时被 {@link com.gametips.platform.module.tool.registry.ToolRegistry}
 * 自动扫描并注册,LLM 通过 function-calling 即可调用。
 *
 * <p>骨架阶段用纯 Java 反射实现,不引 LangChain4j 依赖(§12 第 1 条:先 mock);
 * 接 LangChain4j 时只需把方法列表喂给 {@code ToolSpecification.builder()}。
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Tool {

    /** Tool 名称(给 LLM 看的 function name,缺省取方法名) */
    String name() default "";

    /** Tool 描述(给 LLM 看的,决定它何时被调用,务必清晰) */
    String description();

    /** 风险等级,见 {@link RiskLevel};默认只读 */
    RiskLevel riskLevel() default RiskLevel.READ_ONLY;
}
