package com.gametips.platform.common.config;

import com.gametips.platform.common.security.JwtAuthenticationFilter;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import java.io.IOException;

/**
 * JWT 无状态认证。
 * 公开接口：认证相关、游戏/攻略/评论/地图等只读查询。
 * 写操作与敏感接口需认证，管理员接口通过 @PreAuthorize("hasRole('ADMIN')") 保护。
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final com.gametips.platform.module.oauth.web.OAuth2LoginSuccessHandler oauth2LoginSuccessHandler;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/v1/auth/**", "/error").permitAll()
                        .requestMatchers(HttpMethod.GET, "/uploads/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/games/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/guides/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/articles/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/wiki/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/comments/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/questions/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/tools/maps/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/tools/simulators/**").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/v1/tools/simulators/*/calculate").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/v1/ai/parse/**").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/v1/agent/chat", "/api/v1/agent/chat/**").permitAll()
                        .requestMatchers("/api/v1/agent/**").authenticated()
                        .requestMatchers("/api/v1/rag/reindex").hasRole("ADMIN")
                        .requestMatchers("/api/v1/rag/**").authenticated()
                        .requestMatchers("/oauth2/**", "/login/**").permitAll()
                        // 健康检查与指标端点必须放行：
                        // 否则容器的 HEALTHCHECK 与负载均衡/K8s 探针会拿到 401，
                        // 导致容器被判定 unhealthy 而反复重启。
                        // 只放行只读端点，不放开 /actuator/env、/heapdump 等敏感端点
                        // （暴露面由 application-prod.yml 的 management.endpoints 控制）。
                        .requestMatchers("/actuator/health", "/actuator/health/**").permitAll()
                        .requestMatchers("/actuator/info").permitAll()
                        .requestMatchers("/actuator/metrics/**").permitAll()
                        .anyRequest().authenticated())
                .exceptionHandling(ex -> ex
                        .authenticationEntryPoint((request, response, authException) ->
                                writeJson(response, HttpServletResponse.SC_UNAUTHORIZED,
                                        "{\"code\":1002,\"message\":\"未认证\",\"data\":null}"))
                        .accessDeniedHandler((request, response, deniedException) ->
                                writeJson(response, HttpServletResponse.SC_FORBIDDEN,
                                        "{\"code\":1003,\"message\":\"无权限\",\"data\":null}")))
                .oauth2Login(oauth -> oauth
                        .successHandler(oauth2LoginSuccessHandler))
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    private void writeJson(HttpServletResponse response, int status, String body) throws IOException {
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("UTF-8");
        response.getWriter().write(body);
    }
}
