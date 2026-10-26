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
 * 游戏角色全量数值与机制实体
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "game_character")
public class GameCharacter extends BaseEntity {

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @Column(name = "name", nullable = false, length = 128)
    private String name;

    @Column(name = "title", length = 128)
    private String title;

    @Column(name = "rarity", nullable = false)
    private Integer rarity = 5;

    @Column(name = "element", nullable = false, length = 32)
    private String element;

    @Column(name = "weapon_type", nullable = false, length = 32)
    private String weaponType;

    @Column(name = "region", length = 64)
    private String region;

    @Column(name = "arkhe", length = 32)
    private String arkhe;

    @Column(name = "avatar_url", length = 500)
    private String avatarUrl;

    @Column(name = "splash_url", length = 500)
    private String splashUrl;

    /** 1-90级成长数据（包含生命、基础攻击白值、防御力各阶数值） */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "base_stats", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> baseStats = List.of();

    /** 突破专属成长属性（如暴击率/暴伤/元素增伤等各突破阶数值） */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "special_ascension_stat", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> specialAscensionStat = Map.of();

    /** 突破升级材料消耗清单 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "ascension_materials", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> ascensionMaterials = List.of();

    /** 战斗技能（普攻、战技、爆发）1-10(13)级倍率、冷却时间、能量消耗等 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "talents", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> talents = List.of();

    /** 固有天赋（突破20/60级解锁机制与生活特长） */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "passives", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> passives = List.of();

    /** 命之座 1-6 命效果描述与机制加成 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "constellations", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> constellations = List.of();

    /** 特殊与隐藏机制（ICD附着冷却、元素量、削韧抗打断、生命之契/夜魂值、卡肉参数） */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "special_mechanics", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> specialMechanics = Map.of();

    /** 推荐配装（专武、备选武器、圣遗物套装、主副词条权重） */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "recommendations", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> recommendations = Map.of();

    /** 数据 SHA-256 快照哈希（用于定期巡检与变动比对） */
    @Column(name = "data_hash", nullable = false, length = 64)
    private String dataHash = "";

    /** 适用游戏版本号（如 5.0） */
    @Column(name = "version", nullable = false, length = 32)
    private String version = "5.0";
}
