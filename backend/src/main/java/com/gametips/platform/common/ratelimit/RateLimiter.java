package com.gametips.platform.common.ratelimit;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.data.redis.core.script.RedisScript;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.Collections;

/**
 * Redis 固定窗口限流器（基于原子 Lua 脚本与 Fail-Open 降级）。
 * key: rate:limit:{resource}:{principal}
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RateLimiter {

    private static final RedisScript<Long> LIMIT_SCRIPT = new DefaultRedisScript<>(
            "local current = redis.call('INCR', KEYS[1])\n" +
            "if tonumber(current) == 1 then\n" +
            "    redis.call('EXPIRE', KEYS[1], ARGV[1])\n" +
            "end\n" +
            "return current",
            Long.class
    );

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
        try {
            long expireSeconds = Math.max(1, window.toSeconds());
            Long count = redisTemplate.execute(
                    LIMIT_SCRIPT,
                    Collections.singletonList(key),
                    String.valueOf(expireSeconds)
            );
            return count != null && count <= limit;
        } catch (Exception e) {
            log.warn("[rate-limiter] Redis error, fail-open: resource={}, principal={}, error={}",
                    resource, principal, e.getMessage());
            return true; // Fail-Open: protect availability
        }
    }
}
