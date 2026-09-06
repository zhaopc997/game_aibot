package com.gametips.platform.module.tool.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 标记 Tool 方法的入参(V2 architecture §4.3 参数 schema)。
 *
 * <p>骨架阶段用 description 喂给 LLM 的 function-calling schema;
 * 接 LangChain4j 后会变成 {@code @ToolParam}。
 */
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface ToolParam {

    /** 参数名(英文,给 LLM 看);缺省取形参名 */
    String name() default "";

    /** 参数说明(给 LLM 看,务必清晰,LLM 据此判断如何传值) */
    String description();

    /** 是否必填 */
    boolean required() default true;
}
