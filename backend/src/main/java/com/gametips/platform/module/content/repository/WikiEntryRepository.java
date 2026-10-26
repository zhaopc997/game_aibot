package com.gametips.platform.module.content.repository;

import com.gametips.platform.module.content.domain.WikiEntry;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface WikiEntryRepository extends JpaRepository<WikiEntry, Long> {

    List<WikiEntry> findTop20ByGameIdOrderByLastUpdatedDesc(Long gameId);

    List<WikiEntry> findByTitleContainingIgnoreCase(String keyword);
}
