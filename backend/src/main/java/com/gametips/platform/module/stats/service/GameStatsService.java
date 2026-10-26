package com.gametips.platform.module.stats.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.stats.domain.*;
import com.gametips.platform.module.stats.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class GameStatsService {

    private final GameCharacterRepository characterRepository;
    private final GameWeaponRepository weaponRepository;
    private final GameArtifactSetRepository artifactSetRepository;
    private final GameMechanicRuleRepository mechanicRuleRepository;

    public Page<GameCharacter> listCharacters(Long gameId, String element, Pageable pageable) {
        if (element != null && !element.isBlank()) {
            return characterRepository.findByGameIdAndElement(gameId, element.trim(), pageable);
        }
        return characterRepository.findByGameId(gameId, pageable);
    }

    @org.springframework.cache.annotation.Cacheable(cacheNames = "stats:character", key = "#id")
    public GameCharacter getCharacterById(Long id) {
        return characterRepository.findById(id)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "角色数值档案不存在"));
    }

    @org.springframework.cache.annotation.Cacheable(cacheNames = "stats:character:name", key = "#gameId + ':' + #name")
    public GameCharacter getCharacterByName(Long gameId, String name) {
        return characterRepository.findByGameIdAndName(gameId, name)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "角色 " + name + " 数值档案不存在"));
    }

    public Page<GameWeapon> listWeapons(Long gameId, String type, Pageable pageable) {
        if (type != null && !type.isBlank()) {
            return weaponRepository.findByGameIdAndType(gameId, type.trim(), pageable);
        }
        return weaponRepository.findByGameId(gameId, pageable);
    }

    @org.springframework.cache.annotation.Cacheable(cacheNames = "stats:weapon", key = "#id")
    public GameWeapon getWeaponById(Long id) {
        return weaponRepository.findById(id)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "武器数值档案不存在"));
    }

    public Page<GameArtifactSet> listArtifactSets(Long gameId, Pageable pageable) {
        return artifactSetRepository.findByGameId(gameId, pageable);
    }

    @org.springframework.cache.annotation.Cacheable(cacheNames = "stats:artifact", key = "#id")
    public GameArtifactSet getArtifactSetById(Long id) {
        return artifactSetRepository.findById(id)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "圣遗物套装不存在"));
    }

    public List<GameMechanicRule> listMechanicRules(Long gameId, String category) {
        if (category != null && !category.isBlank()) {
            return mechanicRuleRepository.findByGameIdAndCategory(gameId, category.trim());
        }
        return mechanicRuleRepository.findByGameId(gameId);
    }
}
