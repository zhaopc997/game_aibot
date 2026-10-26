package com.gametips.platform.module.user.repository;

import com.gametips.platform.module.user.domain.UserGameProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserGameProfileRepository extends JpaRepository<UserGameProfile, Long> {

    Optional<UserGameProfile> findByUserIdAndGameId(Long userId, Long gameId);

    List<UserGameProfile> findByUserId(Long userId);
}
