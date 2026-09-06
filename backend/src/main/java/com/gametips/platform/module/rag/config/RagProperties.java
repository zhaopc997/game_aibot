package com.gametips.platform.module.rag.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * V2 AI Copilot RAG 配置项(§4.4-4.6 architecture-v2)。
 * 对应 application.yml 的 app.rag.* 节点。
 */
@ConfigurationProperties(prefix = "app.rag")
public class RagProperties {

    private Embedding embedding = new Embedding();
    private String indexName = "guide_chunks";
    private int topK = 5;
    private boolean useBm25 = true;
    private boolean useKnn = true;

    // ── 子配置 ──

    public static class Embedding {
        private String baseUrl = "https://api.siliconflow.cn/v1";
        private String apiKey = "";
        private String model = "Pro/BAAI/bge-m3";
        private int dim = 1024;
        private int timeoutSeconds = 30;

        public String getBaseUrl() { return baseUrl; }
        public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }
        public String getApiKey() { return apiKey; }
        public void setApiKey(String apiKey) { this.apiKey = apiKey; }
        public String getModel() { return model; }
        public void setModel(String model) { this.model = model; }
        public int getDim() { return dim; }
        public void setDim(int dim) { this.dim = dim; }
        public int getTimeoutSeconds() { return timeoutSeconds; }
        public void setTimeoutSeconds(int timeoutSeconds) { this.timeoutSeconds = timeoutSeconds; }
    }

    public Embedding getEmbedding() { return embedding; }
    public void setEmbedding(Embedding embedding) { this.embedding = embedding; }
    public String getIndexName() { return indexName; }
    public void setIndexName(String indexName) { this.indexName = indexName; }
    public int getTopK() { return topK; }
    public void setTopK(int topK) { this.topK = topK; }
    public boolean isUseBm25() { return useBm25; }
    public void setUseBm25(boolean useBm25) { this.useBm25 = useBm25; }
    public boolean isUseKnn() { return useKnn; }
    public void setUseKnn(boolean useKnn) { this.useKnn = useKnn; }
}
