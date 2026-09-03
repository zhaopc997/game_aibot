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

import java.time.Instant;
import java.time.LocalDate;

/**
 * 游戏版本表。注意：该表无 updated_at，不继承 BaseEntity。
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "game_version")
public class GameVersion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @Column(name = "version_number", nullable = false, length = 32)
    private String versionNumber;

    @Column(name = "release_date")
    private LocalDate releaseDate;

    @Column(name = "patch_notes")
    private String patchNotes;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();
}
