package com.gametips.platform.module.ai.service.llm;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * OpenAI 兼容大模型客户端（SiliconFlow / OpenAI / DeepSeek 等）。
 * 通过 app.ai.provider=openai 启用（配合 app.ai.openai.api-key / base-url / model）。
 * 走 chat/completions 接口，解析 JSON 为结构化攻略步骤。
 */
@Slf4j
@Component
@ConditionalOnProperty(name = "app.ai.provider", havingValue = "openai", matchIfMissing = false)
public class OpenAiLlmClient implements LlmClient {

    /** 失败重试次数(含首次)，网络抖动/5xx 场景下避免直接失败。 */
    private static final int MAX_ATTEMPTS = 3;
    /** 退避基数(ms)，实际等待按 BASE * 2^(n-1) 增长。 */
    private static final long BASE_BACKOFF_MS = 500;

    private final String apiKey;
    private final String baseUrl;
    private final String model;
    private final int requestTimeoutSeconds;
    private final int maxTokens;
    private final HttpClient http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(15)).build();

    public OpenAiLlmClient(
            @Value("${app.ai.openai.api-key:}") String apiKey,
            @Value("${app.ai.openai.base-url:https://api.siliconflow.cn/v1}") String baseUrl,
            @Value("${app.ai.openai.model:gpt-4o-mini}") String model,
            @Value("${app.ai.openai.timeout-seconds:120}") int requestTimeoutSeconds,
            @Value("${app.ai.openai.max-tokens:1500}") int maxTokens) {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.model = model;
        this.requestTimeoutSeconds = requestTimeoutSeconds > 0 ? requestTimeoutSeconds : 120;
        this.maxTokens = maxTokens > 0 ? maxTokens : 1500;
    }

    @Override
    public Map<String, Object> parseGuide(String sourceType, String rawContent) {
        String prompt = """
                你是一名游戏攻略作者。请把下面的素材提炼成一篇结构化的游戏攻略。
                要求：输出 JSON，格式为 {"title":"...","summary":"...","steps":[{"title":"步骤名","description":"详细说明","tips":"小技巧或注意事项"}]}
                步骤 3-6 个，中文，面向新手。素材如下：
                %s
                """.formatted(rawContent == null ? "" : rawContent.substring(0, Math.min(rawContent.length(), 3000)));
        return chatJson(prompt);
    }

    @Override
    public String chat(String question, String context) {
        String prompt = "请结合以下已知攻略回答用户问题：\n" + context + "\n\n用户问题：" + question;
        return chatText(prompt);
    }

    @Override
    public Map<String, Object> generateDraft(String notes) {
        String prompt = """
                你是一名专业游戏攻略作者。请为《%s》撰写一篇新手图文攻略。
                只输出一个 JSON 对象，禁止输出任何其他文字、注释或代码块标记。
                JSON 格式：{"title":"...","summary":"...","steps":[{"title":"步骤名","description":"图文详细说明","tips":"注意事项"}]}
                步骤 5-8 个，中文，内容具体实用、条理清晰，面向刚入坑的玩家。
                """.formatted(notes);
        return chatJson(prompt);
    }

    @Override
    public boolean supportsTools() {
        return apiKey != null && !apiKey.isBlank();
    }

    @Override
    public LlmResponse chatWithTools(List<Map<String, Object>> messages, List<Map<String, Object>> tools) {
        try {
            Map<String, Object> req = new LinkedHashMap<>();
            req.put("model", model);
            req.put("messages", messages);
            if (tools != null && !tools.isEmpty()) {
                req.put("tools", tools);
                req.put("tool_choice", "auto");
            }
            req.put("temperature", 0.7);
            req.put("max_tokens", maxTokens);
            String body = objectMapper.writeValueAsString(req);
            String resp = post(body, false);
            return extractLlmResponse(resp);
        } catch (Exception e) {
            log.warn("[openai-llm] chatWithTools failed: {}", e.getMessage());
            throw new BizException(ErrorCodes.INTERNAL_ERROR, "大模型工具交互失败: " + e.getMessage());
        }
    }

    // ──────────── private ────────────

    private String chatText(String prompt) {
        String body = jsonBody(prompt);
        String resp = post(body, false);
        return extractText(resp);
    }

    private Map<String, Object> chatJson(String prompt) {
        String body = jsonBody(prompt);
        String resp = post(body, true);
        return extractJson(resp);
    }

    private final ObjectMapper objectMapper = new ObjectMapper();

    private String jsonBody(String prompt) {
        try {
            Map<String, Object> req = new java.util.LinkedHashMap<>();
            req.put("model", model);
            req.put("messages", List.of(Map.of("role", "user", "content", prompt)));
            req.put("temperature", 0.7);
            req.put("max_tokens", maxTokens);
            return objectMapper.writeValueAsString(req);
        } catch (Exception e) {
            throw new IllegalStateException("构造请求体失败", e);
        }
    }

    private String post(String body, boolean jsonMode) {
        BizException last = null;
        // 只对可恢复错误重试：4xx(除 429)与业务错误重试无意义，直接抛出
        for (int attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
            try {
                return postOnce(body);
            } catch (BizException e) {
                last = e;
                if (!isRetryable(e) || attempt == MAX_ATTEMPTS) throw e;
                long backoffMs = BASE_BACKOFF_MS * (1L << (attempt - 1));
                log.warn("[openai-llm] 第 {}/{} 次失败({}), {}ms 后重试", attempt, MAX_ATTEMPTS, e.getMessage(), backoffMs);
                try {
                    Thread.sleep(backoffMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw e;
                }
            } catch (Exception e) {
                last = new BizException(ErrorCodes.INTERNAL_ERROR, "LLM 调用失败: " + e.getMessage());
                if (attempt == MAX_ATTEMPTS) throw last;
                long backoffMs = BASE_BACKOFF_MS * (1L << (attempt - 1));
                log.warn("[openai-llm] 第 {}/{} 次异常({}), {}ms 后重试", attempt, MAX_ATTEMPTS, e.getMessage(), backoffMs);
                try {
                    Thread.sleep(backoffMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw last;
                }
            }
        }
        throw last != null ? last : new BizException(ErrorCodes.INTERNAL_ERROR, "LLM 调用失败");
    }

    /** 5xx 与网络瞬时错误可重试；4xx(除 429 限流)是请求本身问题，重试无意义。 */
    private boolean isRetryable(BizException e) {
        String msg = e.getMessage() == null ? "" : e.getMessage();
        if (msg.contains("429")) return true;              // 限流，值得退避重试
        if (msg.matches(".*LLM API 5\\d\\d.*")) return true; // 服务端错误
        return msg.contains("LLM 调用失败");                // 网络/超时类
    }

    private String postOnce(String body) {
        try {
            log.info("[openai-llm] request model={} url={}", model, baseUrl.replaceAll("/+$", "") + "/chat/completions");
            log.debug("[openai-llm] body={}", body);
            HttpRequest req = HttpRequest.newBuilder(URI.create(baseUrl.replaceAll("/+$", "") + "/chat/completions"))
                    .timeout(Duration.ofSeconds(requestTimeoutSeconds))
                    .header("Authorization", "Bearer " + apiKey)
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8))
                    .build();
            HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() / 100 != 2) {
                throw new BizException(ErrorCodes.INTERNAL_ERROR,
                        "LLM API " + resp.statusCode() + ": " + truncate(resp.body(), 300));
            }
            return resp.body();
        } catch (BizException e) {
            throw e;
        } catch (Exception e) {
            throw new BizException(ErrorCodes.INTERNAL_ERROR, "LLM 调用失败: " + e.getMessage());
        }
    }

    private String extractText(String resp) {
        try {
            Map<String, Object> root = new ObjectMapper().readValue(resp, Map.class);
            List<Map<String, Object>> choices = (List<Map<String, Object>>) root.get("choices");
            if (choices == null || choices.isEmpty()) return resp;
            Map<String, Object> msg = (Map<String, Object>) choices.get(0).get("message");
            return String.valueOf(msg.get("content"));
        } catch (Exception e) {
            return resp;
        }
    }

    @SuppressWarnings("unchecked")
    private LlmResponse extractLlmResponse(String resp) {
        try {
            Map<String, Object> root = objectMapper.readValue(resp, Map.class);
            List<Map<String, Object>> choices = (List<Map<String, Object>>) root.get("choices");
            if (choices == null || choices.isEmpty()) {
                return LlmResponse.builder().content(resp).build();
            }
            Map<String, Object> choice = choices.get(0);
            Map<String, Object> message = (Map<String, Object>) choice.get("message");
            if (message == null) {
                return LlmResponse.builder().content(resp).build();
            }

            Object contentObj = message.get("content");
            String content = contentObj != null ? String.valueOf(contentObj) : null;

            List<Map<String, Object>> rawToolCalls = (List<Map<String, Object>>) message.get("tool_calls");
            List<LlmToolCall> toolCalls = new ArrayList<>();
            if (rawToolCalls != null) {
                for (Map<String, Object> tc : rawToolCalls) {
                    String id = (String) tc.get("id");
                    Map<String, Object> func = (Map<String, Object>) tc.get("function");
                    String funcName = func != null ? (String) func.get("name") : null;
                    Map<String, Object> parsedArgs = new HashMap<>();
                    if (func != null && func.get("arguments") != null) {
                        Object rawArgs = func.get("arguments");
                        if (rawArgs instanceof Map<?, ?> m) {
                            parsedArgs = (Map<String, Object>) m;
                        } else if (rawArgs instanceof String s && !s.isBlank()) {
                            try {
                                parsedArgs = objectMapper.readValue(s, Map.class);
                            } catch (Exception ex) {
                                log.warn("[openai-llm] parse tool arguments failed: {}", s);
                            }
                        }
                    }
                    toolCalls.add(LlmToolCall.builder()
                            .id(id)
                            .name(funcName)
                            .arguments(parsedArgs)
                            .build());
                }
            }

            return LlmResponse.builder()
                    .content(content)
                    .toolCalls(toolCalls)
                    .build();
        } catch (Exception e) {
            log.warn("[openai-llm] parse response failed: {}", e.getMessage());
            return LlmResponse.builder().content(resp).build();
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> extractJson(String resp) {
        String text = extractText(resp);
        String json = stripCodeFence(text);
        int s = json.indexOf('{'), e = json.lastIndexOf('}');
        if (s >= 0 && e > s) json = json.substring(s, e + 1);
        try {
            return new ObjectMapper().readValue(json, Map.class);
        } catch (Exception ex) {
            log.warn("[openai-llm] JSON 解析失败，降级为单步骤: {}", ex.getMessage());
            return Map.of("steps", List.of(Map.of("title", "攻略", "description", text)));
        }
    }

    private String stripCodeFence(String s) {
        if (s == null) return "";
        String t = s.trim();
        if (t.startsWith("```json")) t = t.substring(7);
        else if (t.startsWith("```")) t = t.substring(3);
        if (t.endsWith("```")) t = t.substring(0, t.length() - 3);
        return t.trim();
    }

    private String quote(String s) {
        return s == null ? "" : s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "");
    }
    private String truncate(String s, int n) {
        return s == null || s.length() <= n ? s : s.substring(0, n) + "…";
    }
}