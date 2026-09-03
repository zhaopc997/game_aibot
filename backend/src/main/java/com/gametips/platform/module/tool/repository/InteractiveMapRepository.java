package com.gametips.platform.module.tool.repository;

import com.gametips.platform.module.tool.domain.InteractiveMap;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface InteractiveMapRepository extends JpaRepository<InteractiveMap, Long> {

    List<InteractiveMap> findByGameId(Long gameId);
}
