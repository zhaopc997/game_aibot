package com.gametips.platform.module.stats.repository;

import com.gametips.platform.module.stats.domain.GameCharacter;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GameCharacterRepository extends JpaRepository<GameCharacter, Long> {

    List<GameCharacter> findByGameId(Long gameId);

    Page<GameCharacter> findByGameId(Long gameId, Pageable pageable);

    Page<GameCharacter> findByGameIdAndElement(Long gameId, String element, Pageable pageable);

    Optional<GameCharacter> findByGameIdAndName(Long gameId, String name);

    List<GameCharacter> findByNameContainingIgnoreCase(String name);
}
