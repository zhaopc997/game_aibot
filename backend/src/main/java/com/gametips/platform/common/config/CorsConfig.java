package com.gametips.platform.common.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.Arrays;
import java.util.List;

/**
 * CORS 配置。
 *
 * <p>两种部署形态：
 * <ul>
 *   <li><b>同域部署（推荐）</b>：Nginx 托管前端并把 /api 反代到后端，
 *       浏览器视角下只有一个源，<b>无需 CORS</b>。此时 {@code app.cors.allowed-origins} 留空即可。</li>
 *   <li><b>分离部署</b>：前后端不同域名（如 app.example.com / api.example.com），
 *       必须显式配置 {@code CORS_ALLOWED_ORIGINS}，否则浏览器会拦截请求。</li>
 * </ul>
 *
 * <p>安全约束：绝不使用 {@code allowedOrigins("*")} 搭配 {@code allowCredentials(true)}
 * —— 该组合会被 Spring 拒绝，且本身也不安全（等于把带Cookie 的凭证开放给任意站点）。
 * 需要"任意来源"的场景请用 {@code allowedOriginPatterns} 并确保不使用凭证。
 */
@Configuration
public class CorsConfig {

    private static final Logger log = LoggerFactory.getLogger(CorsConfig.class);

    /** 允许的前端来源，逗号分隔。留空表示不启用 CORS（同域部署场景）。 */
    @Value("${app.cors.allowed-origins:}")
    private String allowedOrigins;

    /** 允许的前端来源模式（支持通配），优先级高于 allowed-origins。 */
    @Value("${app.cors.allowed-origin-patterns:}")
    private String allowedOriginPatterns;

    /** 是否允许携带凭证（Cookie/Authorization）。默认关闭。 */
    @Value("${app.cors.allow-credentials:false}")
    private boolean allowCredentials;

    @Bean
    public CorsFilter corsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();

        List<String> origins = splitCsv(allowedOrigins);
        List<String> patterns = splitCsv(allowedOriginPatterns);

        if (!patterns.isEmpty()) {
            // Spring 6 的 setter 签名为 List<String>，不是 String[]
            config.setAllowedOriginPatterns(patterns);
            log.info("[cors] 已启用 allowedOriginPatterns: {}", patterns);
        } else if (!origins.isEmpty()) {
            config.setAllowedOrigins(origins);
            log.info("[cors] 已启用 allowedOrigins: {}", origins);
        } else {
            // 同域部署：不需要 CORS 头。返回一个放行一切的空过滤器，
            // 由Nginx/网关保证同源，避免开发期因未配置导致跨域报错。
            log.info("[cors] 未配置允许来源，按同域部署处理（不注入 CORS 头）");
            return new CorsFilter(source);
        }

        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setExposedHeaders(List.of("Content-Disposition"));
        config.setMaxAge(3600L);
        config.setAllowCredentials(allowCredentials);

        if (allowCredentials && (origins.contains("*") || patterns.contains("*"))) {
            log.warn("[cors] allow-credentials=true 与通配来源同时出现，存在安全风险，请改为精确来源");
        }

        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }

    private List<String> splitCsv(String raw) {
        if (raw == null || raw.isBlank()) {
            return List.of();
        }
        return Arrays.stream(raw.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
    }
}