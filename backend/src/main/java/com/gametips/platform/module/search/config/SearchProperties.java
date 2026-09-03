package com.gametips.platform.module.search.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "app.search")
public class SearchProperties {

    /** pg | elasticsearch */
    private String provider = "pg";
    private Elasticsearch elasticsearch = new Elasticsearch();

    @Data
    public static class Elasticsearch {
        private String uris = "http://localhost:9200";
        private String index = "guides";
        private int bulkSize = 500;
    }
}
