package com.gametips.platform.module.rag.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * RAG 模块总开关。
 * 后续 IndexerService / HybridRetriever 都通过 @Autowired RagProperties 取配置。
 */
@Configuration
@EnableConfigurationProperties(RagProperties.class)
public class RagConfig {
}
