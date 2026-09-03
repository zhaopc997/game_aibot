package com.gametips.platform.common.config;

import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.jsontype.impl.LaissezFaireSubTypeValidator;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

/**
 * Redis 缓存配置（Spring Cache）。
 * 各缓存独立 TTL；过期时间加入随机抖动（±20%）防止缓存雪崩。
 */
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        ObjectMapper mapper = new ObjectMapper()
                .registerModule(new JavaTimeModule())
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        // 启用默认类型信息，保证反序列化时能还原为原类型（而非 LinkedHashMap）。
        // 使用独立 mapper，避免污染 HTTP 序列化用的共享 ObjectMapper。
        mapper.activateDefaultTyping(LaissezFaireSubTypeValidator.instance,
                ObjectMapper.DefaultTyping.NON_FINAL, JsonTypeInfo.As.PROPERTY);
        GenericJackson2JsonRedisSerializer serializer =
                new GenericJackson2JsonRedisSerializer(mapper);
        RedisCacheConfiguration base = RedisCacheConfiguration.defaultCacheConfig()
                .disableCachingNullValues()
                .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(serializer));

        Map<String, RedisCacheConfiguration> configs = new HashMap<>();
        configs.put("guide:detail", base.entryTtl(jittered(Duration.ofMinutes(10))));
        configs.put("guide:list", base.entryTtl(jittered(Duration.ofMinutes(5))));
        configs.put("game:info", base.entryTtl(jittered(Duration.ofHours(1))));
        configs.put("user:info", base.entryTtl(jittered(Duration.ofMinutes(30))));

        return RedisCacheManager.builder(factory)
                .cacheDefaults(base.entryTtl(Duration.ofMinutes(10)))
                .withInitialCacheConfigurations(configs)
                .build();
    }

    /**
     * 在基础 TTL 上叠加 ±20% 随机抖动，防止大量 key 同时过期造成缓存雪崩。
     */
    private Duration jittered(Duration base) {
        long ms = base.toMillis();
        double factor = 1 + (Math.random() * 0.4 - 0.2);
        return Duration.ofMillis((long) (ms * factor));
    }
}
