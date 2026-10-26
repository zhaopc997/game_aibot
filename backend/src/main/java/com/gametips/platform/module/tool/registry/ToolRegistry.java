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
                    || beanClassName.equals(ToolRegistry.class.getName())) {
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

    /**
     * 将注册的工具导出为 OpenAI 标准 Tools (Function Calling) JSON Schema 结构
     */
    public List<Map<String, Object>> toOpenAiTools() {
        List<Map<String, Object>> result = new ArrayList<>();
        for (ToolDefinition def : tools.values()) {
            Map<String, Object> tool = new java.util.LinkedHashMap<>();
            tool.put("type", "function");

            Map<String, Object> function = new java.util.LinkedHashMap<>();
            function.put("name", def.getName());
            function.put("description", def.getDescription() == null ? "" : def.getDescription());

            Map<String, Object> parameters = new java.util.LinkedHashMap<>();
            parameters.put("type", "object");

            Map<String, Object> properties = new java.util.LinkedHashMap<>();
            List<String> required = new ArrayList<>();

            if (def.getParams() != null) {
                for (ToolDefinition.ParamSpec p : def.getParams()) {
                    Map<String, Object> prop = new java.util.LinkedHashMap<>();
                    String typeStr = p.getType() == null ? "string" : p.getType();
                    String jsonType = "string";
                    if ("int".equalsIgnoreCase(typeStr) || "Integer".equalsIgnoreCase(typeStr)
                            || "long".equalsIgnoreCase(typeStr) || "Long".equalsIgnoreCase(typeStr)) {
                        jsonType = "integer";
                    } else if ("double".equalsIgnoreCase(typeStr) || "Double".equalsIgnoreCase(typeStr)
                            || "float".equalsIgnoreCase(typeStr) || "Float".equalsIgnoreCase(typeStr)) {
                        jsonType = "number";
                    } else if ("boolean".equalsIgnoreCase(typeStr) || "Boolean".equalsIgnoreCase(typeStr)) {
                        jsonType = "boolean";
                    } else if ("List".equalsIgnoreCase(typeStr) || typeStr.contains("[]") || typeStr.contains("List")) {
                        jsonType = "array";
                        prop.put("items", Map.of("type", "string"));
                    }
                    prop.put("type", jsonType);
                    if (p.getDescription() != null && !p.getDescription().isBlank()) {
                        prop.put("description", p.getDescription());
                    }
                    properties.put(p.getName(), prop);
                    if (p.isRequired()) {
                        required.add(p.getName());
                    }
                }
            }

            parameters.put("properties", properties);
            if (!required.isEmpty()) {
                parameters.put("required", required);
            }
            function.put("parameters", parameters);
            tool.put("function", function);
            result.add(tool);
        }
        return result;
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

            // 必填校验：缺失或空白直接拒绝，避免把 null 透传给下游造成难以定位的 NPE
            if (ann.required() && isBlank(val)) {
                throw new BizException(ErrorCodes.PARAM_ERROR,
                        "missing required parameter: " + key);
            }
            if (isBlank(val) && !types[i].isPrimitive()) {
                // 可选参数缺省时传 null，避免用 0 / "" 冒充有效值
                result[i] = null;
                continue;
            }
            // 集合/数组的目标元素类型必须从方法签名取（Class 已被擦除）
            result[i] = cast(val, types[i], m.getGenericParameterTypes()[i]);
        }
        return result;
    }

    private static boolean isBlank(Object v) {
        if (v == null) return true;
        if (v instanceof String s) return s.isBlank();
        if (v instanceof java.util.Collection<?> c) return c.isEmpty();
        return false;
    }

    private Object cast(Object v, Class<?> type) {
        return cast(v, type, null);
    }

    private Object cast(Object v, Class<?> type, java.lang.reflect.Type genericType) {
        if (v == null) {
            if (type.isPrimitive()) {
                if (type == boolean.class) return false;
                if (type == int.class) return 0;
                if (type == long.class) return 0L;
                if (type == double.class) return 0.0;
                if (type == float.class) return 0.0f;
            }
            return null;
        }
        if (type.isInstance(v)) return v;
        if (type == String.class) return v.toString();
        if (type == Long.class || type == long.class) {
            if (v instanceof Number num) return num.longValue();
            return Long.parseLong(v.toString().trim());
        }
        if (type == Integer.class || type == int.class) {
            if (v instanceof Number num) return num.intValue();
            return Integer.parseInt(v.toString().trim());
        }
        if (type == Boolean.class || type == boolean.class) {
            if (v instanceof Boolean b) return b;
            return Boolean.parseBoolean(v.toString().trim());
        }
        if (type == Double.class || type == double.class) {
            if (v instanceof Number num) return num.doubleValue();
            return Double.parseDouble(v.toString().trim());
        }
        if (List.class.isAssignableFrom(type)) return convertList(v, genericType);

        // 数组类型（如 String[]）按元素逐个转换
        if (type.isArray() && v instanceof List<?> src) {
            Class<?> comp = type.getComponentType();
            Object arr = java.lang.reflect.Array.newInstance(comp, src.size());
            for (int i = 0; i < src.size(); i++) {
                java.lang.reflect.Array.set(arr, i, cast(src.get(i), comp));
            }
            return arr;
        }
        throw new BizException(ErrorCodes.PARAM_ERROR,
                "unsupported param type: " + type.getSimpleName());
    }

    /**
     * List 参数按目标泛型逐元素转换。
     *
     * <p>直接透传会让 LLM 传来的 List&lt;Integer&gt; 撞上方法签名 List&lt;Long&gt;，
     * 反射调用抛 ArgumentTypeException（LLM 极少给出精确的 Long）。
     *
     * <p>注意：元素类型必须从方法签名的 {@code getGenericParameterTypes()} 取；
     * {@code List.class.getGenericSuperclass()} 对接口返回 null（接口无父类），不可用。
     */
    private Object convertList(Object v, java.lang.reflect.Type genericType) {
        if (!(v instanceof List<?> src)) {
            throw new BizException(ErrorCodes.PARAM_ERROR,
                    "expected a list but got: " + (v == null ? "null" : v.getClass().getSimpleName()));
        }
        Class<?> comp = String.class;
        if (genericType instanceof java.lang.reflect.ParameterizedType pt) {
            java.lang.reflect.Type[] args = pt.getActualTypeArguments();
            if (args.length == 1 && args[0] instanceof Class<?> c && c != Object.class) {
                comp = c;
            }
        }
        List<Object> out = new ArrayList<>(src.size());
        for (Object o : src) {
            out.add(cast(o, comp));
        }
        return out;
    }
}
