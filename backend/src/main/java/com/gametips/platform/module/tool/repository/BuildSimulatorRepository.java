package com.gametips.platform.module.tool.repository;

import com.gametips.platform.module.tool.domain.BuildSimulator;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface BuildSimulatorRepository extends JpaRepository<BuildSimulator, Long> {

    List<BuildSimulator> findByGameId(Long gameId);
}
