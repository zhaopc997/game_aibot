package com.gametips.platform.common.security;

import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final String BEARER_PREFIX = "Bearer ";

    private static final String USER_STATUS_CACHE_PREFIX = "user:status:";
    private static final java.time.Duration USER_STATUS_CACHE_TTL = java.time.Duration.ofMinutes(5);

    private final JwtService jwtService;
    private final com.gametips.platform.module.user.repository.UserRepository userRepository;
    private final org.springframework.data.redis.core.StringRedisTemplate redisTemplate;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith(BEARER_PREFIX)
                && SecurityContextHolder.getContext().getAuthentication() == null) {
            try {
                String token = header.substring(BEARER_PREFIX.length());
                Claims claims = jwtService.parse(token);
                Long userId = Long.valueOf(claims.getSubject());
                String username = claims.get("username", String.class);
                @SuppressWarnings("unchecked")
                List<String> roles = claims.get("roles", List.class);

                // 禁用逻辑：带 Redis 缓存（5 分钟 TTL），降低对 PG 的穿透
                String cacheKey = USER_STATUS_CACHE_PREFIX + userId;
                String status = null;
                try {
                    status = redisTemplate.opsForValue().get(cacheKey);
                } catch (Exception ignored) {}

                if (status == null) {
                    com.gametips.platform.module.user.domain.User user =
                            userRepository.findById(userId).orElse(null);
                    if (user == null) {
                        status = "NOT_FOUND";
                    } else {
                        status = user.getStatus() != null ? user.getStatus().name() : "DISABLED";
                    }
                    try {
                        redisTemplate.opsForValue().set(cacheKey, status, USER_STATUS_CACHE_TTL);
                    } catch (Exception ignored) {}
                }

                if (!"NORMAL".equals(status)) {
                    filterChain.doFilter(request, response);
                    return;
                }

                LoginUser loginUser = new LoginUser(userId, username, roles);
                UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                        loginUser, null, loginUser.getAuthorities());
                auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(auth);
            } catch (Exception ignored) {
                // token 无效/过期：不设置认证上下文，交由 SecurityConfig 判定
            }
        }
        filterChain.doFilter(request, response);
    }
}
