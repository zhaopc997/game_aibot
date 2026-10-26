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
 * 圣遗物套装与词条规格实体
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "game_artifact_set")
public class GameArtifactSet extends BaseEntity {

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @Column(name = "name", nullable = false, length = 128)
    private String name;

    @Column(name = "rarity_min", nullable = false)
    private Integer rarityMin = 4;

    @Column(name = "rarity_max", nullable = false)
    private Integer rarityMax = 5;

    @Column(name = "icon_url", length = 500)
    private String iconUrl;

    @Column(name = "two_piece_bonus", columnDefinition = "text")
    private String twoPieceBonus;

    @Column(name = "four_piece_bonus", columnDefinition = "text")
    private String fourPieceBonus;

    /** 5个部位（生之花、死之羽、时之沙、空之杯、理之冠）信息 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "pieces", nullable = false, columnDefinition = "jsonb")
    private List<Map<String, Object>> pieces = List.of();

    /** 主词条池与副词条4档强化库 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "rules_reference", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> rulesReference = Map.of();

    @Column(name = "data_hash", nullable = false, length = 64)
    private String dataHash = "";

    @Column(name = "version", nullable = false, length = 32)
    private String version = "5.0";
}
