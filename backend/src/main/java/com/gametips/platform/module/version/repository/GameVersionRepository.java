package com.gametips.platform.module.version.repository;

import com.gametips.platform.module.version.domain.GameVersion;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface GameVersionRepository extends JpaRepository<GameVersion, Long> {

    List<GameVersion> findByGameIdOrderByCreatedAtDesc(Long gameId);

    Optional<GameVersion> findByGameIdAndVersionNumber(Long gameId, String versionNumber);
}
