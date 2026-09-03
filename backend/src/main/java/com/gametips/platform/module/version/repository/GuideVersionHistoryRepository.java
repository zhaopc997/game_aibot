package com.gametips.platform.module.version.repository;

import com.gametips.platform.module.version.domain.GuideVersionHistory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface GuideVersionHistoryRepository extends JpaRepository<GuideVersionHistory, Long> {

    List<GuideVersionHistory> findByGuideIdOrderByUpdatedAtDesc(Long guideId);

    Optional<GuideVersionHistory> findTopByGuideIdAndVersionIdOrderByUpdatedAtDesc(Long guideId, Long versionId);
}
