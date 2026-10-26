package com.gametips.platform.module.stats.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.api.PageResult;
import com.gametips.platform.module.stats.domain.*;
import com.gametips.platform.module.stats.service.GameStatsService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/games/{gameId}")
@RequiredArgsConstructor
public class GameStatsController {

    private final GameStatsService statsService;

    @GetMapping("/characters")
    public ApiResponse<PageResult<GameCharacter>> listCharacters(
            @PathVariable Long gameId,
            @RequestParam(required = false) String element,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<GameCharacter> result = statsService.listCharacters(gameId, element, PageRequest.of(page, size));
        return ApiResponse.ok(PageResult.of(result.getContent(), result.hasNext() ? String.valueOf(page + 1) : null));
    }

    @GetMapping("/characters/{id}")
    public ApiResponse<GameCharacter> getCharacterDetail(
            @PathVariable Long gameId,
            @PathVariable Long id) {
        return ApiResponse.ok(statsService.getCharacterById(id));
    }

    @GetMapping("/characters/name/{name}")
    public ApiResponse<GameCharacter> getCharacterByName(
            @PathVariable Long gameId,
            @PathVariable String name) {
        return ApiResponse.ok(statsService.getCharacterByName(gameId, name));
    }

    @GetMapping("/weapons")
    public ApiResponse<PageResult<GameWeapon>> listWeapons(
            @PathVariable Long gameId,
            @RequestParam(required = false) String type,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<GameWeapon> result = statsService.listWeapons(gameId, type, PageRequest.of(page, size));
        return ApiResponse.ok(PageResult.of(result.getContent(), result.hasNext() ? String.valueOf(page + 1) : null));
    }

    @GetMapping("/weapons/{id}")
    public ApiResponse<GameWeapon> getWeaponDetail(
            @PathVariable Long gameId,
            @PathVariable Long id) {
        return ApiResponse.ok(statsService.getWeaponById(id));
    }

    @GetMapping("/artifacts")
    public ApiResponse<PageResult<GameArtifactSet>> listArtifactSets(
            @PathVariable Long gameId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<GameArtifactSet> result = statsService.listArtifactSets(gameId, PageRequest.of(page, size));
        return ApiResponse.ok(PageResult.of(result.getContent(), result.hasNext() ? String.valueOf(page + 1) : null));
    }

    @GetMapping("/artifacts/{id}")
    public ApiResponse<GameArtifactSet> getArtifactSetDetail(
            @PathVariable Long gameId,
            @PathVariable Long id) {
        return ApiResponse.ok(statsService.getArtifactSetById(id));
    }

    @GetMapping("/mechanics")
    public ApiResponse<List<GameMechanicRule>> listMechanicRules(
            @PathVariable Long gameId,
            @RequestParam(required = false) String category) {
        return ApiResponse.ok(statsService.listMechanicRules(gameId, category));
    }
}
