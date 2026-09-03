package com.gametips.platform.common.ratelimit;

import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;

/**
 * Redis 固定窗口限流器。
 * key: rate:limit:{resource}:{principal}
 */
@Component
@RequiredArgsConstructor
public class RateLimiter {

    private final StringRedisTemplate redisTemplate;

    /**
     * @param resource  限流资源名（如 default、ai）
     * @param principal 限流主体（用户ID/IP）
     * @param window    窗口时长
     * @param limit     窗口内最大请求数
     * @return 是否允许通过
     */
    public boolean allow(String resource, String principal, Duration window, int limit) {
        String key = "rate:limit:" + resource + ":" + principal;
        Long count = redisTemplate.opsForValue().increment(key);
        if (count != null && count == 1L) {
            redisTemplate.expire(key, window);
        }
        return count != null && count <= limit;
    }
}
