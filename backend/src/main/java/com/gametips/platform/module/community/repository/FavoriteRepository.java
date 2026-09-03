package com.gametips.platform.module.community.repository;

import com.gametips.platform.module.community.domain.Favorite;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface FavoriteRepository extends JpaRepository<Favorite, Long> {

    Optional<Favorite> findByTargetTypeAndTargetIdAndUserId(String targetType, Long targetId, Long userId);

    List<Favorite> findTop50ByUserIdOrderByCreatedAtDesc(Long userId);
}
