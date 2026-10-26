package com.gametips.platform.common.ratelimit;

import com.gametips.platform.common.security.LoginUser;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.nio.charset.StandardCharsets;
import java.time.Duration;

/**
 * 统一限流拦截器：
 * 默认资源 60 次/分钟；AI 类接口 10 次/分钟。
 * 主体优先取用户ID，未登录取客户端 IP。
 */
@Component
@RequiredArgsConstructor
public class RateLimitInterceptor implements HandlerInterceptor {

    private static final Duration DEFAULT_WINDOW = Duration.ofMinutes(1);
    private static final int DEFAULT_LIMIT = 1000;
    private static final int AI_LIMIT = 10;

    private final RateLimiter rateLimiter;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        String uri = request.getRequestURI();
        boolean isAi = uri.startsWith("/api/v1/ai") || uri.startsWith("/api/v1/agent");
        String resource = isAi ? "ai" : "default";
        int limit = isAi ? AI_LIMIT : DEFAULT_LIMIT;

        String principal = principal(request);
        if (!rateLimiter.allow(resource, principal, DEFAULT_WINDOW, limit)) {
            response.setStatus(429);
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.setCharacterEncoding(StandardCharsets.UTF_8.name());
            response.getWriter().write("{\"code\":3001,\"message\":\"请求过于频繁，请稍后再试\",\"data\":null}");
            return false;
        }
        return true;
    }

    private String principal(HttpServletRequest request) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof LoginUser loginUser) {
            return "u" + loginUser.userId();
        }
        String clientIp = request.getHeader("X-Real-IP");
        if (clientIp == null || clientIp.isBlank()) {
            clientIp = request.getRemoteAddr();
        }
        if (clientIp != null) {
            clientIp = clientIp.replaceAll("[^a-zA-Z0-9.:%_-]", "");
        }
        return "ip:" + (clientIp == null || clientIp.isBlank() ? "unknown" : clientIp);
    }
}
