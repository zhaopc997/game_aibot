package com.gametips.platform.module.rag.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

/**
 * 启动后给 ES 索引注册自定义 ngram analyzer + 重建 mapping。
 *
 * 标准 ES 镜像不带 ik 中文分词,但 ES 自带 ngram tokenizer 配合 lowercase
 * filter 可以实现简单的中文 substring 检索(3-5 字 ngram)。
 *
 * 这一步独立于 IndexerService,即使 IndexerService 没跑,索引也建好了。
 */
@Slf4j
@Component
public class ElasticsearchIndexBootstrap {

    private final String esUri;
    private final String indexName;
    private final HttpClient http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5)).build();
    private final ObjectMapper json = new ObjectMapper();

    public ElasticsearchIndexBootstrap(
            @Value("${spring.elasticsearch.uris:http://localhost:9200}") String esUri,
            @Value("${app.rag.index-name:guide_chunks}") String indexName) {
        // uris 可能含多个,取第一个
        this.esUri = esUri.split(",")[0].trim().replaceAll("/$", "");
        this.indexName = indexName;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void onApplicationReady() {
        bootstrap();
    }

    public synchronized void bootstrap() {
        try {
            // 1. 检查索引是否已存在
            if (indexExists()) {
                log.info("[es-bootstrap] 索引 {} 已存在,跳过创建", indexName);
                return;
            }
            log.info("[es-bootstrap] 创建索引 {} (含 ngram analyzer)", indexName);

            // 2. settings + mapping 一起发
            String body = """
                {
                  "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                      "analyzer": {
                        "ngram_analyzer": {
                          "type": "custom",
                          "tokenizer": "ngram_tok",
                          "filter": ["lowercase"]
                        }
                      },
                      "tokenizer": {
                        "ngram_tok": {
                          "type": "ngram",
                          "min_gram": 2,
                          "max_gram": 3,
                          "token_chars": ["letter", "digit"]
                        }
                      }
                    }
                  },
                  "mappings": {
                    "properties": {
                      "guideId":   { "type": "long" },
                      "gameId":    { "type": "long" },
                      "versionId": { "type": "long" },
                      "title":     { "type": "text", "analyzer": "ngram_analyzer", "search_analyzer": "ngram_analyzer" },
                      "summary":   { "type": "text", "analyzer": "ngram_analyzer", "search_analyzer": "ngram_analyzer" },
                      "text":      { "type": "text", "analyzer": "ngram_analyzer", "search_analyzer": "ngram_analyzer" },
                      "status":    { "type": "keyword" },
                      "tags":      { "type": "keyword" },
                      "updatedAt": { "type": "date", "format": "date_time" },
                      "sourceUrl": { "type": "keyword" },
                      "embedding": { "type": "dense_vector", "dims": 1024, "index": true, "similarity": "cosine" }
                    }
                  }
                }
                """;
            HttpRequest req = HttpRequest.newBuilder(URI.create(esUri + "/" + indexName))
                    .header("Content-Type", "application/json")
                    .PUT(HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8))
                    .build();
            HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() / 100 == 2) {
                log.info("[es-bootstrap] ✅ 索引创建成功: {}", indexName);
            } else {
                log.warn("[es-bootstrap] ❌ 创建失败: {} - {}", resp.statusCode(), resp.body());
            }
        } catch (Exception e) {
            log.warn("[es-bootstrap] 引导失败(ES 未启动?): {}", e.getMessage());
        }
    }

    private boolean indexExists() throws Exception {
        HttpResponse<String> r = http.send(
                HttpRequest.newBuilder(URI.create(esUri + "/" + indexName))
                        .method("HEAD", HttpRequest.BodyPublishers.noBody()).build(),
                HttpResponse.BodyHandlers.ofString());
        return r.statusCode() == 200;
    }
}
