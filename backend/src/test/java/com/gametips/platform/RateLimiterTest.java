package com.gametips.platform;

import com.gametips.platform.common.ratelimit.RateLimiter;
import org.junit.jupiter.api.Test;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.RedisScript;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class RateLimiterTest {

    @Test
    void shouldAllowWhenUnderLimit() {
        StringRedisTemplate redisTemplate = mock(StringRedisTemplate.class);
        when(redisTemplate.execute(any(RedisScript.class), anyList(), any())).thenReturn(1L);

        RateLimiter limiter = new RateLimiter(redisTemplate);
        boolean allowed = limiter.allow("test", "user1", Duration.ofMinutes(1), 5);
        assertThat(allowed).isTrue();
    }

    @Test
    void shouldDenyWhenOverLimit() {
        StringRedisTemplate redisTemplate = mock(StringRedisTemplate.class);
        when(redisTemplate.execute(any(RedisScript.class), anyList(), any())).thenReturn(6L);

        RateLimiter limiter = new RateLimiter(redisTemplate);
        boolean allowed = limiter.allow("test", "user1", Duration.ofMinutes(1), 5);
        assertThat(allowed).isFalse();
    }

    @Test
    void shouldFailOpenWhenRedisThrowsException() {
        StringRedisTemplate redisTemplate = mock(StringRedisTemplate.class);
        when(redisTemplate.execute(any(RedisScript.class), anyList(), any()))
                .thenThrow(new RuntimeException("Redis connection refused"));

        RateLimiter limiter = new RateLimiter(redisTemplate);
        // 遇到 Redis 异常时 Fail-Open，返回 true 确保主流程不被阻断
        boolean allowed = limiter.allow("test", "user1", Duration.ofMinutes(1), 5);
        assertThat(allowed).isTrue();
    }
}
