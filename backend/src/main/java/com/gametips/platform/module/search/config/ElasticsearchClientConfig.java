package com.gametips.platform.module.search.config;

import co.elastic.clients.json.JsonpMapper;
import co.elastic.clients.json.jackson.JacksonJsonpMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 为 Elasticsearch Java 客户端提供正确的 JSON 映射器。
 *
 * <h3>为什么必须显式配置</h3>
 * Spring Boot 的 {@code ElasticsearchClientConfigurations.JacksonJsonpMapperConfiguration}
 * 内部实现是：
 * <pre>
 *   JacksonJsonpMapper jacksonJsonpMapper() {
 *       return new JacksonJsonpMapper();   // ← 无参构造，用的是裸 ObjectMapper
 *   }
 * </pre>
 * 这个裸 ObjectMapper <b>没有注册 JSR-310 模块</b>，因此任何含
 * {@link java.time.Instant} / {@link java.time.LocalDate} 等字段的文档
 * 在写入索引时都会抛：
 * <pre>
 *   InvalidDefinitionException: Java 8 date/time type `java.time.Instant`
 *   not supported by default: add Module "jackson-datatype-jsr310"
 * </pre>
 *
 * <p>本项目 {@code GuideDocument.updatedAt} 正是 {@code Instant}，
 * 导致全部攻略索引写入失败。而 {@code GuideIndexService.index()} 内部
 * 用 try/catch 吞掉了异常，只在日志里留一行
 * {@code index guide N failed}，同时 {@code fullRebuild()} 仍然照常打印
 * {@code indexed=30}（统计的是"尝试条数"而非"成功条数"），
 * 所以故障被完全掩盖，表现为：搜索与 AI 检索长期返回空结果，
 * 而日志看起来一切正常。
 *
 * <h3>修复方式</h3>
 * 复用 Spring 容器中已注册 JSR-310 的 {@link ObjectMapper}
 * （见 {@code common.config.JacksonConfig}）。
 * 自动配置类带 {@code @ConditionalOnMissingBean(JsonpMapper.class)}，
 * 因此本 bean 存在时它会自动退让，不会冲突。
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass({ JsonpMapper.class, ObjectMapper.class })
public class ElasticsearchClientConfig {

    @Bean
    @ConditionalOnMissingBean(JsonpMapper.class)
    public JsonpMapper jsonpMapper(ObjectMapper objectMapper) {
        // 关键：传入 Spring 管理的 ObjectMapper（已注册 JavaTimeModule），
        // 而不是 new JacksonJsonpMapper() 的裸实例。
        return new JacksonJsonpMapper(objectMapper);
    }
}