package com.gametips.platform.module.stats.domain;

import com.gametips.platform.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.Map;

/**
 * 游戏底层战斗规则与特殊机制实体
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "game_mechanic_rule")
public class GameMechanicRule extends BaseEntity {

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    /** 机制分类：DAMAGE_FORMULA / LEVEL_MULTIPLIER / ICD_SYSTEM / POISE_SYSTEM / REGION_SYSTEM */
    @Column(name = "category", nullable = false, length = 64)
    private String category;

    @Column(name = "title", nullable = false, length = 128)
    private String title;

    @Column(name = "formula", columnDefinition = "text")
    private String formula;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "parameters", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> parameters = Map.of();
}
