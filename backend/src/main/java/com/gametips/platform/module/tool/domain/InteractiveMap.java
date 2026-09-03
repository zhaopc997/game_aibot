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

import java.util.List;
import java.util.Map;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "interactive_map")
public class InteractiveMap extends BaseEntity {

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @Column(name = "name", nullable = false, length = 128)
    private String name;

    @Column(name = "map_image_url", length = 500)
    private String mapImageUrl;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "markers", columnDefinition = "jsonb")
    private List<Map<String, Object>> markers = new java.util.ArrayList<>();
}
