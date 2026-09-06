package com.gametips.platform.module.rag.service;

import com.gametips.platform.module.rag.client.EmbeddingClient;
import com.gametips.platform.module.rag.config.RagProperties;
import com.gametips.platform.module.rag.dto.RagHit;
import com.gametips.platform.module.rag.dto.RagQuery;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * RAG 混合检索器(§4.4 architecture-v2)。
 *
 * 实现选择:为彻底避开 Spring Data ES 与 ES Java Client 的版本兼容问题,
 * 我们直接用 JDK HttpClient 打 ES REST API。简单可控。
 *
 * 策略:
 *   - BM25 全文(title^3 + text^2 + summary),ngram analyzer 已生效
 *   - KNN 向量(dense_vector cosine)可选(无 embedding key 时跳过)
 *   - RRF 融合(简化版:BM25 优先,knn 补缺)
 *
 * 降级:任何异常返回空列表,前端有 mock 兜底
 */
@Slf4j
@Service
public class HybridRetriever {

    private final EmbeddingClient embeddingClient;
    private final RagProperties props;

    @Value("${spring.elasticsearch.uris:http://localhost:9201}")
    private String esUri;

    private final String indexName;
    private final HttpClient http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5)).build();
    private final ObjectMapper json = new ObjectMapper();

    public HybridRetriever(EmbeddingClient embeddingClient, RagProperties props,
                            @Value("${app.rag.index-name:guide_chunks}") String indexName) {
        this.embeddingClient = embeddingClient;
        this.props = props;
        this.indexName = indexName;
    }

    public List<RagHit> retrieve(RagQuery q) {
        if (q.getQuery() == null || q.getQuery().isBlank()) {
            return List.of();
        }
        try {
            Long gameId = parseLongOrNull(q.getGameId());
            int topK = q.getTopK() > 0 ? q.getTopK() : props.getTopK();

            // 1) BM25
            List<RagHit> bm25 = searchBm25(q.getQuery(), gameId, topK);

            // 2) KNN(可选,需要 embedding key)
            List<RagHit> knn = List.of();
            if (props.isUseKnn() && embeddingClient.isEnabled()) {
                knn = searchKnn(q.getQuery(), gameId, topK);
            }

            // 3) 简化 RRF
            List<RagHit> merged = mergeUnique(bm25, knn, topK);
            log.info("[retriever] q='{}' gameId={} → bm25={} knn={} merged={}",
                    truncate(q.getQuery(), 30), gameId, bm25.size(), knn.size(), merged.size());
            return merged;
        } catch (Exception e) {
            log.error("[retriever] 检索失败: {}", e.getMessage());
            return List.of();
        }
    }

    /** BM25 全文检索 */
    private List<RagHit> searchBm25(String query, Long gameId, int topK) {
        try {
            // 用 Jackson 构建 JSON,避免手拼字符串嵌套错误
            com.fasterxml.jackson.databind.node.ObjectNode root = json.createObjectNode();
            root.put("size", topK);
            root.set("_source", json.createArrayNode().add("title").add("summary").add("text")
                    .add("gameId").add("status").add("sourceUrl"));

            com.fasterxml.jackson.databind.node.ObjectNode boolQ = json.createObjectNode();
            com.fasterxml.jackson.databind.node.ArrayNode mustArr = json.createArrayNode();
            com.fasterxml.jackson.databind.node.ObjectNode mm = json.createObjectNode();
            mm.put("query", query);
            com.fasterxml.jackson.databind.node.ArrayNode fields = json.createArrayNode();
            fields.add("title^3"); fields.add("text^2"); fields.add("summary");
            mm.set("fields", fields);
            mm.put("type", "best_fields");
            mustArr.add(json.createObjectNode().set("multi_match", mm));
            if (gameId != null) {
                mustArr.add(json.createObjectNode().set("term",
                        json.createObjectNode().put("gameId", gameId)));
            }
            boolQ.set("must", mustArr);
            root.set("query", json.createObjectNode().set("bool", boolQ));

            String resp = post("/" + indexName + "/_search", root.toString());
            return parseHits(resp, topK);
        } catch (Exception e) {
            log.warn("[retriever] BM25 查询失败: {}", e.getMessage());
            return List.of();
        }
    }

    /** KNN 向量检索 */
    private List<RagHit> searchKnn(String query, Long gameId, int topK) {
        try {
            float[] vec = embeddingClient.embedOne(query);
            if (vec.length == 0) return List.of();
            com.fasterxml.jackson.databind.node.ObjectNode root = json.createObjectNode();
            root.put("size", topK);
            root.set("_source", json.createArrayNode().add("title").add("summary").add("text")
                    .add("gameId").add("status").add("sourceUrl"));

            com.fasterxml.jackson.databind.node.ObjectNode knn = json.createObjectNode();
            knn.put("field", "embedding");
            knn.set("query_vector", json.readTree(toVectorJson(vec)));
            knn.put("k", topK);
            knn.put("num_candidates", Math.max(50, topK * 10));
            if (gameId != null) {
                knn.set("filter", json.createObjectNode().set("term",
                        json.createObjectNode().put("gameId", gameId)));
            }
            root.set("knn", knn);

            String resp = post("/" + indexName + "/_search", root.toString());
            return parseHits(resp, topK);
        } catch (Exception e) {
            log.warn("[retriever] KNN 查询失败: {}", e.getMessage());
            return List.of();
        }
    }

    // ───── HTTP ─────

    private String post(String path, String body) throws Exception {
        String url = esUri.split(",")[0].trim().replaceAll("/$", "") + path;
        HttpRequest req = HttpRequest.newBuilder(URI.create(url))
                .timeout(Duration.ofSeconds(props.getEmbedding().getTimeoutSeconds()))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8))
                .build();
        HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() / 100 != 2) {
            throw new RuntimeException("ES " + resp.statusCode() + ": " + truncate(resp.body(), 200));
        }
        return resp.body();
    }

    @SuppressWarnings("unchecked")
    private List<RagHit> parseHits(String resp, int topK) throws Exception {
        JsonNode root = json.readTree(resp);
        JsonNode hits = root.path("hits").path("hits");
        if (!hits.isArray()) return List.of();
        List<RagHit> out = new ArrayList<>();
        for (JsonNode h : hits) {
            JsonNode src = h.path("_source");
            RagHit hit = new RagHit();
            hit.setGuideId(src.path("guideId").asLong());
            hit.setTitle(src.path("title").asText());
            hit.setGameId(src.path("gameId").isMissingNode() || src.path("gameId").isNull()
                    ? null : String.valueOf(src.path("gameId").asLong()));
            hit.setVersion(src.path("status").asText());
            hit.setSnippet(truncate(
                    src.path("summary").isMissingNode() ? src.path("text").asText() : src.path("summary").asText(),
                    200));
            hit.setAnchor(h.path("_id").asText());
            hit.setScore(h.path("_score").asDouble());
            hit.setUrl(src.path("sourceUrl").isMissingNode() || src.path("sourceUrl").isNull()
                    ? ("/guides/" + hit.getGuideId())
                    : src.path("sourceUrl").asText());
            out.add(hit);
        }
        return out.stream().limit(topK).collect(Collectors.toList());
    }

    // ───── helpers ─────

    private List<RagHit> mergeUnique(List<RagHit> primary, List<RagHit> secondary, int topK) {
        List<RagHit> out = new ArrayList<>(topK);
        Set<String> seen = new HashSet<>();
        for (RagHit h : primary) {
            if (seen.add(h.getGuideId() + ":" + h.getTitle())) out.add(h);
        }
        for (RagHit h : secondary) {
            if (seen.add(h.getGuideId() + ":" + h.getTitle())) out.add(h);
        }
        return out.stream().limit(topK).collect(Collectors.toList());
    }

    private static String escapeJson(String s) {
        return s == null ? "" : s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
    }

    private static String toVectorJson(float[] arr) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < arr.length; i++) {
            if (i > 0) sb.append(',');
            sb.append(arr[i]);
        }
        return sb.append("]").toString();
    }

    private static Long parseLongOrNull(String s) {
        if (s == null || s.isBlank()) return null;
        try { return Long.parseLong(s.trim()); } catch (Exception e) { return null; }
    }

    private static String truncate(String s, int n) {
        return s == null || s.length() <= n ? s : s.substring(0, n) + "…";
    }
}
