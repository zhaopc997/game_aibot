package com.gametips.platform.common.trace;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

/**
 * 全局 traceId 注入 Filter。
 *
 * <p>优先级最高(在 Security 之前),保证所有请求(无论是否鉴权)都有 traceId。
 * 同时把 traceId 写回响应头 {@code X-Trace-Id} 便于前端联调。
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class TraceIdFilter extends OncePerRequestFilter {

    public static final String HEADER = "X-Trace-Id";

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        // 优先使用上游传入的 traceId,便于跨服务调用串联
        String incoming = request.getHeader(HEADER);
        String traceId = (incoming != null && !incoming.isBlank())
                ? incoming
                : TraceContext.init();
        try {
            response.setHeader(HEADER, traceId);
            chain.doFilter(request, response);
        } finally {
            TraceContext.clear();
        }
    }
}
