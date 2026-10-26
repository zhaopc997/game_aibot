package com.gametips.platform.module.content.domain;

import com.gametips.platform.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

/**
 * 资讯/专栏文章。
 */
@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "article")
public class Article extends BaseEntity {

    @Column(name = "game_id")
    private Long gameId;

    @Column(name = "title", nullable = false, length = 255)
    private String title;

    @Column(name = "author_id", nullable = false)
    private Long authorId;

    @Column(name = "category", length = 64)
    private String category;

    @Column(name = "content", columnDefinition = "text")
    private String content;

    @Column(name = "published_at")
    private Instant publishedAt;

    @Column(name = "status", nullable = false, length = 32)
    private String status = "PUBLISHED";
}
