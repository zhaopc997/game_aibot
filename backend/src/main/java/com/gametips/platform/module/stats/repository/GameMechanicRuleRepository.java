package com.gametips.platform.module.stats.repository;

import com.gametips.platform.module.stats.domain.GameMechanicRule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GameMechanicRuleRepository extends JpaRepository<GameMechanicRule, Long> {

    List<GameMechanicRule> findByGameId(Long gameId);

    List<GameMechanicRule> findByGameIdAndCategory(Long gameId, String category);

    Optional<GameMechanicRule> findByGameIdAndCategoryAndTitle(Long gameId, String category, String title);
}
