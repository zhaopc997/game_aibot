package com.gametips.platform.module.community.repository;

import com.gametips.platform.module.community.domain.Question;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface QuestionRepository extends JpaRepository<Question, Long> {

    /** 按游戏筛选 */
    List<Question> findTop50ByGameIdOrderByCreatedAtDesc(Long gameId);

    /**
     * 不按游戏筛选（全站最新）。
     *
     * 注意：不能直接用上面那个方法传 null —— Spring Data 会生成
     * `game_id = NULL`，而 SQL 中 `= NULL` 永远为 false，
     * 导致"不传 gameId 时列表恒为空"（本项目线上曾因此让问答页始终无内容）。
     */
    List<Question> findTop50ByOrderByCreatedAtDesc();
}
