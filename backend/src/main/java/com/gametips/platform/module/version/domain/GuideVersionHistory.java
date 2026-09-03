package com.gametips.platform.module.version.domain;

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
import java.util.Map;

/**
 * 攻略版本历史快照（用于差分对比）。
 * 注意：该表无 created_at，不继承 BaseEntity。
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "guide_version_history")
public class GuideVersionHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "guide_id", nullable = false)
    private Long guideId;

    @Column(name = "version_id")
    private Long versionId;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "content_snapshot", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> contentSnapshot;

    @Column(name = "updated_by")
    private Long updatedBy;

    @Column(name = "updated_at", nullable = false, updatable = false)
    private Instant updatedAt = Instant.now();
}
