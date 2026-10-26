package com.gametips.platform.module.stats.repository;

import com.gametips.platform.module.stats.domain.GameArtifactSet;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GameArtifactSetRepository extends JpaRepository<GameArtifactSet, Long> {

    List<GameArtifactSet> findByGameId(Long gameId);

    Page<GameArtifactSet> findByGameId(Long gameId, Pageable pageable);

    Optional<GameArtifactSet> findByGameIdAndName(Long gameId, String name);

    List<GameArtifactSet> findByNameContainingIgnoreCase(String name);
}
