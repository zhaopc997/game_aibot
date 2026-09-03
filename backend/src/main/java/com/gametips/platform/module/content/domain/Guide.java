package com.gametips.platform.module.content.domain;

import com.gametips.platform.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.Map;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "guide")
public class Guide extends BaseEntity {

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @Column(name = "version_id")
    private Long versionId;

    @Column(name = "title", nullable = false, length = 255)
    private String title;

    @Column(name = "author_id", nullable = false)
    private Long authorId;

    @Column(name = "type", nullable = false, length = 32)
    private String type = "MANUAL";

    @Column(name = "difficulty", length = 16)
    private String difficulty;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "tags")
    private java.util.List<String> tags = new java.util.ArrayList<>();

    @Column(name = "summary")
    private String summary;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "content", columnDefinition = "jsonb")
    private Map<String, Object> content = Map.of("steps", java.util.List.of());

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 32)
    private GuideStatus status = GuideStatus.DRAFT;

    @Column(name = "like_count", nullable = false)
    private Long likeCount = 0L;

    @Column(name = "useful_count", nullable = false)
    private Long usefulCount = 0L;

    @Column(name = "verify_count", nullable = false)
    private Long verifyCount = 0L;
}
