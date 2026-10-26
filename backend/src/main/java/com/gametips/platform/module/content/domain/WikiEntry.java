package com.gametips.platform.module.content.domain;

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

/**
 * 游戏百科条目。
 * 注：wiki_entry 表无 created_at/updated_at 列，故不继承 BaseEntity。
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "wiki_entry")
public class WikiEntry {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "game_id", nullable = false)
    private Long gameId;

    @Column(name = "title", nullable = false, length = 255)
    private String title;

    @Column(name = "content", columnDefinition = "text")
    private String content;

    @Column(name = "last_updated")
    private Instant lastUpdated;

    @Column(name = "version_id")
    private Long versionId;
}
