package com.gametips.platform.module.user.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

/**
 * Refresh Token 记录（只存摘要，不存原文）。
 *
 * <p>用于实现三件事：
 * <ol>
 *   <li><b>轮换</b>：每次刷新后旧记录 {@code revokedAt} 被置位，旧令牌立即失效；</li>
 *   <li><b>复用检测</b>：已吊销的令牌再次出现，说明令牌被复制过，吊销该用户全部令牌；</li>
 *   <li><b>主动吊销</b>：登出、改密、封号时可让令牌立即失效（JWT 本身无状态，做不到这点）。</li>
 * </ol>
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "refresh_token")
public class RefreshToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    /** JWT 原文的 sha256 十六进制摘要 */
    @Column(name = "token_hash", nullable = false, length = 64)
    private String tokenHash;

    @Column(name = "issued_at", nullable = false, updatable = false)
    private Instant issuedAt = Instant.now();

    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    /** 非空表示已失效（轮换或吊销） */
    @Column(name = "revoked_at")
    private Instant revokedAt;

    /** 轮换后的后继令牌摘要 */
    @Column(name = "replaced_by", length = 64)
    private String replacedBy;

    @Column(name = "client_ip", length = 64)
    private String clientIp;

    @Column(name = "user_agent", length = 255)
    private String userAgent;

    public boolean isActive() {
        return revokedAt == null && expiresAt.isAfter(Instant.now());
    }
}
