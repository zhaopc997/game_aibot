package com.gametips.platform.module.version.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.version.domain.Game;
import com.gametips.platform.module.version.domain.GameVersion;
import com.gametips.platform.module.version.event.GameVersionUpdatedEvent;
import com.gametips.platform.module.version.repository.GameRepository;
import com.gametips.platform.module.version.repository.GameVersionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class GameService {

    private final GameRepository gameRepository;
    private final GameVersionRepository gameVersionRepository;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public Game create(Game game) {
        game.setId(null);
        return gameRepository.save(game);
    }

    @org.springframework.cache.annotation.Cacheable(cacheNames = "game:info", key = "#id")
    public Game get(Long id) {
        return gameRepository.findById(id)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "游戏不存在"));
    }

    public java.util.List<Game> listAll() {
        return gameRepository.findAll();
    }

    /**
     * 版本更新入口：写入 game_version 记录、更新 current_version，
     * 发布 GameVersionUpdatedEvent 触发攻略过期检测与作者通知。
     */
    @org.springframework.cache.annotation.CacheEvict(cacheNames = "game:info", key = "#id")
    @Transactional
    public Game updateCurrentVersion(Long id, String newVersion, String patchNotes) {
        Game game = get(id);
        if (game.getCurrentVersion() != null && game.getCurrentVersion().equals(newVersion)) {
            throw new BizException(ErrorCodes.CONFLICT, "当前已是该版本");
        }
        GameVersion gv = gameVersionRepository
                .findByGameIdAndVersionNumber(id, newVersion)
                .orElseGet(() -> {
                    GameVersion v = new GameVersion();
                    v.setGameId(id);
                    v.setVersionNumber(newVersion);
                    v.setPatchNotes(patchNotes);
                    return gameVersionRepository.save(v);
                });
        game.setCurrentVersion(newVersion);
        game = gameRepository.save(game);

        eventPublisher.publishEvent(new GameVersionUpdatedEvent(game.getId(), gv.getId(), newVersion));
        return game;
    }
}
