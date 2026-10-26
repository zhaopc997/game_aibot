package com.gametips.platform.module.ai.repository;

import com.gametips.platform.module.ai.domain.AiParseTask;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AiParseTaskRepository extends JpaRepository<AiParseTask, Long> {

    Optional<AiParseTask> findBySourceHash(String sourceHash);

    java.util.List<AiParseTask> findByStatus(com.gametips.platform.module.ai.domain.AiTaskStatus status);
}
