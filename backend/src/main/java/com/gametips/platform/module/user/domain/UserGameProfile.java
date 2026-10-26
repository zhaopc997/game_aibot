package com.gametips.platform.module.user.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.Map;

/**
 * 用户游戏档案 (与 user_game_profile 表映射)。
 * 记录玩家在特定游戏中的角色池、练度、进度等长期特征，可直接对接到 AI 偏好与长期记忆。
 */
@Entity
@Table(name = "user_game_profile", uniqueConstraints = {
        @UniqueConstraint(columnNames = {"user_id", "game_id"})
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserGameProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "role_info", nullable = false, columnDefinition = "jsonb")
    @Builder.Default
    private Map<String, Object> roleInfo = Map.of();

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "progress", nullable = false, columnDefinition = "jsonb")
    @Builder.Default
    private Map<String, Object> progress = Map.of();

    @Column(name = "updated_at", nullable = false)
    @Builder.Default
    private Instant updatedAt = Instant.now();
}
