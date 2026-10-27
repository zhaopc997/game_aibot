package com.gametips.platform.common.security;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.user.domain.RefreshToken;
import com.gametips.platform.module.user.repository.RefreshTokenRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.HexFormat;
import java.util.Optional;

/**
 * Refresh Token 的生命周期管理：签发、轮换、复用检测、吊销。
 *
 * <h3>为什么必须有这一层</h3>
 * JWT 是无状态的，服务端本来无法让已签发的令牌失效。这对 Refresh Token 是致命的：
 * 它有效期长（7 天），一旦泄露，攻击者可以持续换取 Access Token，
 * 而用户既无法察觉，也无法「登出」。
 *
 * <p>因此这里在服务端保存令牌摘要，把「刷新」变成一次性动作：
 * <ul>
 *   <li>每次刷新 → 旧令牌立即作废，签发新令牌（轮换）；</li>
 *   <li>已作废的令牌再次被使用 → 说明它被复制过（正常客户端不会重复使用旧令牌），
 *       按泄露处理，吊销该用户全部令牌并强制重新登录。</li>
 * </ul>
 *
 * <p>只存 SHA-256 摘要：数据库泄露时攻击者无法反推出可用的令牌原文。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class RefreshTokenService {

    private final RefreshTokenRepository repository;
    private final JwtService jwtService;

    /**
     * 签发新的 Refresh Token 并落库。
     *
     * @return JWT 原文（只此一次出现在响应里，库里只有摘要）
     */
    @Transactional
    public String issue(Long userId, String clientIp, String userAgent) {
        String token = jwtService.generateRefreshToken(userId);
        RefreshToken row = new RefreshToken();
        row.setUserId(userId);
        row.setTokenHash(sha256(token));
        row.setExpiresAt(jwtService.extractExpiration(token));
        row.setClientIp(truncate(clientIp, 64));
        row.setUserAgent(truncate(userAgent, 255));
        repository.save(row);
        return token;
    }

    /**
     * 轮换：校验旧令牌 → 作废旧记录 → 签发新令牌。
     *
     * @throws BizException 令牌无效/过期/已被吊销（含复用检测命中）
     */
    @Transactional
    public String rotate(String oldToken, String clientIp, String userAgent) {
        Long userId;
        try {
            userId = jwtService.extractUserId(oldToken);
        } catch (Exception e) {
            // 签名错误、格式错误、已过期，一律视为无效令牌
            throw new BizException(ErrorCodes.UNAUTHORIZED, "登录状态已失效，请重新登录");
        }

        String hash = sha256(oldToken);
        Optional<RefreshToken> found = repository.findByTokenHash(hash);
        if (found.isEmpty()) {
            // 签名合法但库里没有：可能是本功能上线前签发的老令牌。
            // 不放行 —— 否则老令牌可以绕过轮换机制继续无限使用。
            throw new BizException(ErrorCodes.UNAUTHORIZED, "登录状态已失效，请重新登录");
        }

        RefreshToken row = found.get();

        if (row.getRevokedAt() != null) {
            // ★ 复用检测：已被轮换作废的令牌又被使用。
            // 正常客户端换到新令牌后不会再拿旧令牌请求，
            // 因此这几乎必然意味着令牌被复制（XSS、日志泄露、设备被拿走）。
            log.warn("[auth] 检测到 Refresh Token 复用，疑似泄露，吊销该用户全部令牌: userId={}, ip={}",
                    row.getUserId(), clientIp);
            repository.revokeAllByUserId(row.getUserId(), Instant.now());
            throw new BizException(ErrorCodes.UNAUTHORIZED, "登录状态异常，请重新登录");
        }

        if (!row.isActive()) {
            throw new BizException(ErrorCodes.UNAUTHORIZED, "登录状态已失效，请重新登录");
        }

        String newToken = jwtService.generateRefreshToken(userId);

        // 旧记录作废，并指向后继，便于追溯令牌链
        row.setRevokedAt(Instant.now());
        row.setReplacedBy(sha256(newToken));
        repository.save(row);

        RefreshToken next = new RefreshToken();
        next.setUserId(userId);
        next.setTokenHash(sha256(newToken));
        next.setExpiresAt(jwtService.extractExpiration(newToken));
        next.setClientIp(truncate(clientIp, 64));
        next.setUserAgent(truncate(userAgent, 255));
        repository.save(next);

        return newToken;
    }

    /** 登出：吊销该用户全部令牌（JWT 无状态，只能整批失效） */
    @Transactional
    public int revokeAll(Long userId) {
        int n = repository.revokeAllByUserId(userId, Instant.now());
        log.info("[auth] 已吊销用户 {} 的 {} 个 Refresh Token", userId, n);
        return n;
    }

    /** 每天清理过期记录，避免表无限增长 */
    @Scheduled(cron = "0 30 4 * * *")
    @Transactional
    public void cleanupExpired() {
        int n = repository.deleteExpiredBefore(Instant.now().minusSeconds(86_400));
        if (n > 0) {
            log.info("[auth] 已清理 {} 条过期 Refresh Token 记录", n);
        }
    }

    private static String sha256(String s) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(md.digest(s.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 不可用", e);
        }
    }

    private static String truncate(String s, int max) {
        if (s == null) {
            return null;
        }
        return s.length() <= max ? s : s.substring(0, max);
    }
}
