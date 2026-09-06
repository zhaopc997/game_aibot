package com.gametips.platform.module.tool.registry;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.tool.annotation.Tool;
import com.gametips.platform.module.tool.annotation.ToolParam;
import com.gametips.platform.module.tool.dto.ToolDefinition;
import com.gametips.platform.module.tool.dto.ToolResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.aop.support.AopUtils;
import org.springframework.context.ApplicationContext;
import org.springframework.core.annotation.AnnotatedElementUtils;
import org.springframework.stereotype.Component;
import org.springframework.util.ReflectionUtils;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Tool 注册中心(V2 architecture §4.3)。
 *
 * <p>职责:
 * <ol>
 *   <li>应用启动时扫描所有 Spring Bean,收集带 {@link Tool} 注解的方法,写入 {@link #tools}</li>
 *   <li>提供 {@link #invoke(String, Map)} 反射调用入口</li>
 *   <li>提供 {@link #list()} 给 {@code GET /api/v1/agent/tools} 调试用</li>
 * </ol>
 *
 * <p>骨架阶段纯反射实现,不引 LangChain4j;
 * 接 LangChain4j 时替换为 {@code AiServices.toolMetadata()} 自动同步。
 */
@Slf4j
@Component
public class ToolRegistry {

    /** name → ToolDefinition */
    private final Map<String, ToolDefinition> tools = new ConcurrentHashMap<>();

    private final ApplicationContext ctx;

    public ToolRegistry(ApplicationContext ctx) {
        this.ctx = ctx;
        // 扫描延后到 ContextRefreshedEvent,此时所有 bean 都已初始化完毕,
        // 不会触发循环依赖;同时仍早于第一个 HTTP 请求。
    }

    @org.springframework.context.event.EventListener(
        org.springframework.context.event.ContextRefreshedEvent.class)
    public void scan() {
        if (!tools.isEmpty()) return;  // 防止重复调用
        for (String beanName : ctx.getBeanDefinitionNames()) {
            String beanClassName = ctx.getBean(beanName).getClass().getName();
            if (beanClassName.startsWith("com.gametips.platform.module.agent.")
                    || beanClassName.startsWith("com.gametips.platform.module.tool.")) {
                continue;
            }
            Object bean = ctx.getBean(beanName);
            Class<?> targetClass = AopUtils.getTargetClass(bean);
            ReflectionUtils.doWithMethods(targetClass, method -> {
                Tool toolAnn = AnnotatedElementUtils.findMergedAnnotation(method, Tool.class);
                if (toolAnn == null) return;
                register(bean, method, toolAnn);
            });
        }
        log.info("[tool-registry] registered {} tools: {}", tools.size(), tools.keySet());
    }

    private void register(Object bean, Method method, Tool toolAnn) {
        String name = toolAnn.name().isEmpty() ? method.getName() : toolAnn.name();
        if (tools.containsKey(name)) {
            log.warn("[tool-registry] duplicate tool name '{}', overwrite", name);
        }
        List<ToolDefinition.ParamSpec> params = new ArrayList<>();
        addParams(method, params);

        tools.put(name, ToolDefinition.builder()
                .name(name)
                .description(toolAnn.description())
                .riskLevel(toolAnn.riskLevel())
                .params(params)
                .method(method)
                .bean(bean)
                .build());
    }

    private void addParams(Method method, List<ToolDefinition.ParamSpec> params) {
        Class<?>[] paramTypes = method.getParameterTypes();
        String[] paramNames = paramNamesOf(method);
        for (int i = 0; i < paramTypes.length; i++) {
            ToolParam ann = method.getParameters()[i].getAnnotation(ToolParam.class);
            if (ann == null) continue;  // 跳过非 @ToolParam 标注的参数(如 userId 上下文)
            String pname = ann.name().isEmpty() ? paramNames[i] : ann.name();
            params.add(ToolDefinition.ParamSpec.builder()
                    .name(pname)
                    .type(paramTypes[i].getSimpleName())
                    .description(ann.description())
                    .required(ann.required())
                    .build());
        }
    }

    /** 通过 -parameters 编译选项取形参名;取不到回退 arg0/arg1 */
    private String[] paramNamesOf(Method method) {
        String[] names = new String[method.getParameterCount()];
        java.lang.reflect.Parameter[] ps = method.getParameters();
        for (int i = 0; i < ps.length; i++) {
            names[i] = ps[i].isNamePresent() ? ps[i].getName() : ("arg" + i);
        }
        return names;
    }

    /** 列出所有 Tool(供 GET /api/v1/agent/tools) */
    public List<ToolDefinition> list() {
        return new ArrayList<>(tools.values());
    }

    /** 反射调用一个 Tool(骨架阶段,真实阶段改 LangChain4j function-calling) */
    public ToolResult invoke(String name, Map<String, Object> args) {
        ToolDefinition def = tools.get(name);
        if (def == null) {
            return ToolResult.fail("tool not found: " + name, 0);
        }
        long t0 = System.currentTimeMillis();
        try {
            Object[] callArgs = resolveArgs(def, args);
            Object out = def.getMethod().invoke(def.getBean(), callArgs);
            return ToolResult.ok(out, System.currentTimeMillis() - t0);
        } catch (Exception e) {
            log.error("[tool-registry] invoke failed tool={}", name, e);
            return ToolResult.fail(e.getMessage(), System.currentTimeMillis() - t0);
        }
    }

    private Object[] resolveArgs(ToolDefinition def, Map<String, Object> args) {
        Method m = def.getMethod();
        Class<?>[] types = m.getParameterTypes();
        Object[] result = new Object[types.length];
        java.lang.reflect.Parameter[] ps = m.getParameters();
        for (int i = 0; i < ps.length; i++) {
            ToolParam ann = ps[i].getAnnotation(ToolParam.class);
            if (ann == null) {
                // 上下文参数(如 userId),由 Agent 注入;骨架阶段传 null
                result[i] = null;
                continue;
            }
            String key = ann.name().isEmpty() ? ps[i].getName() : ann.name();
            Object val = args == null ? null : args.get(key);
            result[i] = cast(val, types[i]);
        }
        return result;
    }

    private Object cast(Object v, Class<?> type) {
        if (v == null) return null;
        if (type == String.class) return v.toString();
        if (type == Long.class || type == long.class) return ((Number) v).longValue();
        if (type == Integer.class || type == int.class) return ((Number) v).intValue();
        if (type == Boolean.class || type == boolean.class) return v;
        if (type == Double.class || type == double.class) return ((Number) v).doubleValue();
        if (List.class.isAssignableFrom(type)) return v;
        throw new BizException(ErrorCodes.PARAM_ERROR,
                "unsupported param type: " + type.getSimpleName());
    }
}
