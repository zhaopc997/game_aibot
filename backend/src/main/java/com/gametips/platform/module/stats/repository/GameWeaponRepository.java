package com.gametips.platform.module.stats.repository;

import com.gametips.platform.module.stats.domain.GameWeapon;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GameWeaponRepository extends JpaRepository<GameWeapon, Long> {

    List<GameWeapon> findByGameId(Long gameId);

    Page<GameWeapon> findByGameId(Long gameId, Pageable pageable);

    Page<GameWeapon> findByGameIdAndType(Long gameId, String type, Pageable pageable);

    Optional<GameWeapon> findByGameIdAndName(Long gameId, String name);

    List<GameWeapon> findByNameContainingIgnoreCase(String name);
}
