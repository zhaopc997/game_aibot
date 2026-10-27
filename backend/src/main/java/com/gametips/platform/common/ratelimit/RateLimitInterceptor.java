package com.gametips.platform.common.ratelimit;

import com.gametips.platform.common.security.ClientIpResolver;
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
 * 统一限流拦截器。
 *
 * <h3>为什么登录/注册必须单独限流</h3>
 * 初版对所有接口统一 1000 次/分钟 —— 对浏览类接口合适，但对认证接口
 * 等于没有防护：攻击者每分钟可尝试 1000 个密码，足以完成在线撞库。
 * 这类接口的价值密度远高于普通读接口，必须单独收紧：
 * <table>
 *   <tr><th>接口</th><th>限制</th><th>原因</th></tr>
 *   <tr><td>POST /auth/login</td><td>10 次/分钟</td><td>正常用户不会高频登录；配合账号维度锁定抵御撞库</td></tr>
 *   <tr><td>POST /auth/register</td><td>5 次/小时</td><td>阻止批量注册薅积分、刷内容</td></tr>
 *   <tr><td>POST /auth/refresh</td><td>30 次/分钟</td><td>正常刷新频率很低，收紧可限制令牌滥用</td></tr>
 *   <tr><td>AI / Agent</td><td>10 次/分钟</td><td>单次调用成本高</td></tr>
 *   <tr><td>其他</td><td>600 次/分钟</td><td>浏览类接口，防脚本爬取</td></tr>
 * </table>
 *
 * <p>注意：这是<b>按 IP</b> 的粗粒度限流。分布式撞库可以换 IP 绕过，
 * 因此还需要 {@code LoginAttemptService} 的按账号锁定配合，两者互补。
 */
@Component
@RequiredArgsConstructor
public class RateLimitInterceptor implements HandlerInterceptor {

    private static final int DEFAULT_LIMIT = 600;
    private static final int AI_LIMIT = 10;
    private static final int LOGIN_LIMIT = 10;
    // 取 10 而非报告建议的 5：同一出口 IP（学校/公司 NAT）可能有多个真实用户，
    // 过严会误伤；配合下面的账号维度锁定，防刷效果不受影响
    private static final int REGISTER_LIMIT = 10;
    private static final int REFRESH_LIMIT = 30;

    private final RateLimiter rateLimiter;

    /** 限流规则：资源名、窗口、上限 */
    private record Rule(String resource, Duration window, int limit) {
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        Rule rule = ruleFor(request);
        String principal = principal(request);

        if (!rateLimiter.allow(rule.resource(), principal, rule.window(), rule.limit())) {
            reject(response, rule);
            return false;
        }
        return true;
    }

    private Rule ruleFor(HttpServletRequest request) {
        String uri = request.getRequestURI();
        String method = request.getMethod();

        if ("POST".equalsIgnoreCase(method)) {
            if (uri.equals("/api/v1/auth/login")) {
                return new Rule("login", Duration.ofMinutes(1), LOGIN_LIMIT);
            }
            if (uri.equals("/api/v1/auth/register")) {
                return new Rule("register", Duration.ofHours(1), REGISTER_LIMIT);
            }
            if (uri.equals("/api/v1/auth/refresh")) {
                return new Rule("refresh", Duration.ofMinutes(1), REFRESH_LIMIT);
            }
        }
        if (uri.startsWith("/api/v1/ai") || uri.startsWith("/api/v1/agent")) {
            return new Rule("ai", Duration.ofMinutes(1), AI_LIMIT);
        }
        return new Rule("default", Duration.ofMinutes(1), DEFAULT_LIMIT);
    }

    private String principal(HttpServletRequest request) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof LoginUser loginUser) {
            return "u" + loginUser.userId();
        }
        // 必须取真实客户端 IP：若退化成 Docker 网关地址，
        // 全站用户会共用一个限流配额，一人触发即全体被挡
        String clientIp = ClientIpResolver.resolve(request);
        clientIp = clientIp.replaceAll("[^a-zA-Z0-9.:%_-]", "");
        return "ip:" + (clientIp.isBlank() ? "unknown" : clientIp);
    }

    private void reject(HttpServletResponse response, Rule rule) throws Exception {
        response.setStatus(429);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        // Retry-After 让客户端（和爬虫）知道多久后可以再试，减少盲目重试
        response.setHeader("Retry-After", String.valueOf(Math.max(1, rule.window().toSeconds())));
        response.getWriter().write(
                "{\"code\":3001,\"message\":\"请求过于频繁，请稍后再试\",\"data\":null}");
    }
}
