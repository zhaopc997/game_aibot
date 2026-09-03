package com.gametips.platform.module.community.repository;

import com.gametips.platform.module.community.domain.Like;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface LikeRepository extends JpaRepository<Like, Long> {

    boolean existsByTargetTypeAndTargetIdAndUserId(String targetType, Long targetId, Long userId);

    Optional<Like> findByTargetTypeAndTargetIdAndUserId(String targetType, Long targetId, Long userId);

    long countByTargetTypeAndTargetId(String targetType, Long targetId);
}
