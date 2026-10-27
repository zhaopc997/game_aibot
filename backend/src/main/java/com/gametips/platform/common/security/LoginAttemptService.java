package com.gametips.platform.common.security;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;

/**
 * 登录失败锁定（防在线撞库 / 密码喷洒）。
 *
 * <h3>为什么限流之外还需要它</h3>
 * 单纯的「每 IP 每分钟 N 次」挡不住分布式撞库（攻击者换 IP 即可），
 * 也挡不住对单个账号的慢速爆破（每分钟 1 次，永远不触发限流）。
 * 因此这里以「账号」为主维度累计失败次数，与按 IP 的限流互补：
 * <ul>
 *   <li>同一账号连续失败 10 次 → 锁定 15 分钟（无论来自多少 IP）；</li>
 *   <li>同一 IP 失败 30 次 → 锁定 15 分钟（覆盖乱猜用户名的场景）。</li>
 * </ul>
 *
 * <p>计数存 Redis 并带 TTL，锁定会自动解除，无需人工干预。
 * Redis 不可用时 <b>不阻断登录</b>（fail-open）——可用性优先，
 * 此时仍有一层按 IP 的限流兜底。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class LoginAttemptService {

    /** 单账号允许的连续失败次数 */
    private static final int MAX_FAILS_PER_ACCOUNT = 10;
    /** 单 IP 允许的失败次数 */
    private static final int MAX_FAILS_PER_IP = 30;
    /** 统计窗口 = 锁定时长 */
    private static final Duration WINDOW = Duration.ofMinutes(15);

    private final StringRedisTemplate redis;

    /**
     * 登录前检查是否已被锁定，锁定则直接拒绝（不校验密码，避免继续消耗）。
     */
    public void assertNotLocked(String username, String ip) {
        if (isLocked("auth:fail:user:" + normalize(username), MAX_FAILS_PER_ACCOUNT)
                || isLocked("auth:fail:ip:" + normalize(ip), MAX_FAILS_PER_IP)) {
            throw new BizException(ErrorCodes.RATE_LIMITED,
                    "登录失败次数过多，请 15 分钟后再试");
        }
    }

    /** 记录一次失败 */
    public void recordFailure(String username, String ip) {
        bump("auth:fail:user:" + normalize(username));
        bump("auth:fail:ip:" + normalize(ip));
    }

    /** 登录成功后清零该账号的失败计数 */
    public void clearFailures(String username, String ip) {
        try {
            // IP 计数不清零：避免攻击者用一个成功登录来重置 IP 维度的累计
            redis.delete("auth:fail:user:" + normalize(username));
        } catch (Exception e) {
            log.debug("[auth] 清理失败计数出错: {}", e.getMessage());
        }
    }

    private boolean isLocked(String key, int max) {
        try {
            String v = redis.opsForValue().get(key);
            return v != null && Integer.parseInt(v) >= max;
        } catch (Exception e) {
            log.warn("[auth] 读取失败计数出错，放行（fail-open）: {}", e.getMessage());
            return false;
        }
    }

    private void bump(String key) {
        try {
            Long n = redis.opsForValue().increment(key);
            if (n != null && n == 1L) {
                // 首次计数时设置窗口，之后保持同一窗口不续期，
                // 避免攻击者持续尝试导致窗口永不过期（反而把自己锁死更久）
                redis.expire(key, WINDOW);
            }
        } catch (Exception e) {
            log.warn("[auth] 写入失败计数出错: {}", e.getMessage());
        }
    }

    private static String normalize(String s) {
        if (s == null) {
            return "unknown";
        }
        // 防止特殊字符污染 Redis key
        return s.trim().toLowerCase().replaceAll("[^a-z0-9@._:%-]", "_");
    }
}
