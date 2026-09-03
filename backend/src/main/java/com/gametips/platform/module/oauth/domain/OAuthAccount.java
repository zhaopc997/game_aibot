package com.gametips.platform.module.oauth.domain;

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
 * 第三方登录关联。注意：该表无 updated_at，不继承 BaseEntity。
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "oauth_account")
public class OAuthAccount {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "provider", nullable = false, length = 32)
    private String provider;

    @Column(name = "external_id", nullable = false, length = 128)
    private String externalId;

    @Column(name = "external_username", length = 128)
    private String externalUsername;

    @Column(name = "avatar_url", length = 500)
    private String avatarUrl;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();
}
