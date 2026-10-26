package com.gametips.platform.module.content.repository;

import com.gametips.platform.module.content.domain.Article;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ArticleRepository extends JpaRepository<Article, Long> {

    List<Article> findTop20ByGameIdAndStatusOrderByPublishedAtDesc(Long gameId, String status);

    List<Article> findTop20ByStatusOrderByPublishedAtDesc(String status);
}
