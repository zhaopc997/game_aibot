package com.gametips.platform.module.stats.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * 游戏数值版本巡检审计与变动日志实体
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "stat_version_audit")
public class StatVersionAudit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    /** 目标类型：CHARACTER / WEAPON / ARTIFACT / MECHANIC */
    @Column(name = "target_type", nullable = false, length = 32)
    private String targetType;

    @Column(name = "target_id")
    private Long targetId;

    @Column(name = "target_name", nullable = false, length = 128)
    private String targetName;

    @Column(name = "check_batch_no", nullable = false, length = 64)
    private String checkBatchNo;

    /** 状态：UNCHANGED / MODIFIED / NEW_ADDED */
    @Column(name = "status", nullable = false, length = 32)
    private String status;

    @Column(name = "diff_summary", columnDefinition = "text")
    private String diffSummary;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "diff_detail", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> diffDetail = List.of();

    @Column(name = "old_hash", length = 64)
    private String oldHash;

    @Column(name = "new_hash", length = 64)
    private String newHash;

    @Column(name = "checked_at", nullable = false)
    private Instant checkedAt = Instant.now();
}
