package com.gametips.platform.module.rag.client;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.rag.config.RagProperties;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;
import java.util.Map;

/**
 * Embedding 客户端(§4.6 LLM Client 部分)。
 *
 * 调 SiliconFlow 兼容 OpenAI 的 /v1/embeddings 接口。
 * 失败策略:重试 2 次(指数退避 1s/3s),仍败抛 BizException。
 *
 * 注意:留空 API key 时,embed() 返回空数组,让上层降级走 BM25-only。
 */
@Slf4j
@Component
public class EmbeddingClient {

    private final RagProperties.Embedding cfg;
    private final HttpClient http;

    public EmbeddingClient(RagProperties props) {
        this.cfg = props.getEmbedding();
        this.http = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
    }

    public boolean isEnabled() {
        return cfg.getApiKey() != null && !cfg.getApiKey().isBlank();
    }

    /**
     * 批量 embed。多条文本合并为一次请求,省 RTT。
     * @return 顺序与输入一致的 float[] 列表
     */
    public List<float[]> embed(List<String> texts) {
        if (!isEnabled()) {
            log.debug("[embedding] API key 未配置,跳过(降级 BM25-only)");
            return List.of();
        }
        if (texts == null || texts.isEmpty()) {
            return List.of();
        }

        // OpenAI 兼容请求体
        StringBuilder body = new StringBuilder(256 + texts.size() * 200);
        body.append("{\"model\":\"").append(cfg.getModel()).append("\",\"input\":[");
        for (int i = 0; i < texts.size(); i++) {
            if (i > 0) body.append(',');
            body.append('"').append(escape(texts.get(i))).append('"');
        }
        body.append("]}");

        String url = cfg.getBaseUrl().replaceAll("/+$", "") + "/embeddings";
        String resp = postWithRetry(url, body.toString(), 2);

        return parseVectors(resp, texts.size());
    }

    public float[] embedOne(String text) {
        List<float[]> r = embed(List.of(text));
        return r.isEmpty() ? new float[0] : r.get(0);
    }

    // ──────────── private ────────────

    private String postWithRetry(String url, String body, int maxRetry) {
        Exception lastErr = null;
        for (int attempt = 0; attempt <= maxRetry; attempt++) {
            try {
                HttpRequest req = HttpRequest.newBuilder(URI.create(url))
                        .timeout(Duration.ofSeconds(cfg.getTimeoutSeconds()))
                        .header("Authorization", "Bearer " + cfg.getApiKey())
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8))
                        .build();
                HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
                if (resp.statusCode() / 100 == 2) {
                    return resp.body();
                }
                lastErr = new BizException(ErrorCodes.INTERNAL_ERROR,
                        "Embedding API " + resp.statusCode() + ": " + truncate(resp.body(), 200));
            } catch (Exception e) {
                lastErr = e;
                log.warn("[embedding] attempt {} failed: {}", attempt + 1, e.getMessage());
            }
            sleepBackoff(attempt);
        }
        throw new BizException(ErrorCodes.INTERNAL_ERROR,
                "Embedding 调用失败: " + (lastErr != null ? lastErr.getMessage() : "未知"));
    }

    private void sleepBackoff(int attempt) {
        try { Thread.sleep(1000L * (long) Math.pow(3, attempt)); } catch (InterruptedException ignored) {}
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    static class EmbeddingResp {
        @JsonProperty("data") public List<Data> data;
        @JsonIgnoreProperties(ignoreUnknown = true)
        static class Data {
            @JsonProperty("embedding") public List<Double> embedding;
            @JsonProperty("index")    public int index;
        }
    }

    @SuppressWarnings("unchecked")
    private List<float[]> parseVectors(String resp, int expected) {
        try {
            Map<String, Object> root = new com.fasterxml.jackson.databind.ObjectMapper()
                    .readValue(resp, Map.class);
            List<Map<String, Object>> data = (List<Map<String, Object>>) root.get("data");
            if (data == null || data.isEmpty()) return List.of();

            // 按 index 排序
            float[][] arr = new float[expected][];
            for (Map<String, Object> item : data) {
                int idx = ((Number) item.getOrDefault("index", 0)).intValue();
                List<Number> emb = (List<Number>) item.get("embedding");
                if (emb == null) continue;
                float[] vec = new float[emb.size()];
                for (int i = 0; i < emb.size(); i++) vec[i] = emb.get(i).floatValue();
                if (idx >= 0 && idx < expected) arr[idx] = vec;
            }
            List<float[]> out = new java.util.ArrayList<>(expected);
            for (float[] v : arr) out.add(v == null ? new float[0] : v);
            return out;
        } catch (Exception e) {
            throw new BizException(ErrorCodes.INTERNAL_ERROR, "解析 embedding 失败: " + e.getMessage());
        }
    }

    private String escape(String s) {
        return s == null ? "" : s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
    }
    private String truncate(String s, int n) {
        return s == null || s.length() <= n ? s : s.substring(0, n) + "…";
    }
}
