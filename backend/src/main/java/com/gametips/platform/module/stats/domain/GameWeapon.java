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

import java.util.List;
import java.util.Map;

/**
 * 游戏武器全量数值与精炼成长实体
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "game_weapon")
public class GameWeapon extends BaseEntity {

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @Column(name = "name", nullable = false, length = 128)
    private String name;

    @Column(name = "type", nullable = false, length = 32)
    private String type;

    @Column(name = "rarity", nullable = false)
    private Integer rarity = 5;

    @Column(name = "icon_url", length = 500)
    private String iconUrl;

    /** 1-90级基础攻击力白值阶梯 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "base_atk_curve", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> baseAtkCurve = List.of();

    /** 副词条类型与1-90级数值成长 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "sub_stat", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> subStat = Map.of();

    /** 1-5阶精炼被动技能描述与数值增长梯度 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "refinements", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> refinements = List.of();

    /** 突破材料消耗清单 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "ascension_materials", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> ascensionMaterials = List.of();

    @Column(name = "data_hash", nullable = false, length = 64)
    private String dataHash = "";

    @Column(name = "version", nullable = false, length = 32)
    private String version = "5.0";
}
