package com.gametips.platform.module.recommend.repository;

import com.gametips.platform.module.recommend.domain.UserBehaviorLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UserBehaviorLogRepository extends JpaRepository<UserBehaviorLog, Long> {

    List<UserBehaviorLog> findTop100ByUserIdOrderByCreatedAtDesc(Long userId);
}
