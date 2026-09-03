package com.gametips.platform.module.version.domain;

import com.gametips.platform.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "game")
public class Game extends BaseEntity {

    @Column(name = "name", nullable = false, length = 128)
    private String name;

    @Column(name = "alias", length = 255)
    private String alias;

    @Column(name = "platform", length = 64)
    private String platform;

    @Column(name = "category", length = 64)
    private String category;

    @Column(name = "cover_url", length = 500)
    private String coverUrl;

    @Column(name = "description")
    private String description;

    @Column(name = "current_version", length = 32)
    private String currentVersion;
}
