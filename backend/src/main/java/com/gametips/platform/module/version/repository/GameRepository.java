package com.gametips.platform.module.version.repository;

import com.gametips.platform.module.version.domain.Game;
import org.springframework.data.jpa.repository.JpaRepository;

public interface GameRepository extends JpaRepository<Game, Long> {
}
