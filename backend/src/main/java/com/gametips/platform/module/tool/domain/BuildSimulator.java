package com.gametips.platform.module.tool.domain;

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

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "build_simulator")
public class BuildSimulator extends BaseEntity {

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @Column(name = "name", nullable = false, length = 128)
    private String name;

    /** 配置 JSON：属性定义、装备槽位、计算公式参数等 */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "config", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> config = Map.of();
}
