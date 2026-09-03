package com.gametips.platform.module.version.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.module.version.domain.Game;
import com.gametips.platform.module.version.service.GameService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/games")
@RequiredArgsConstructor
public class GameController {

    private final GameService gameService;

    @GetMapping
    public ApiResponse<java.util.List<Game>> list() {
        return ApiResponse.ok(gameService.listAll());
    }

    @GetMapping("/{id}")
    public ApiResponse<Game> detail(@PathVariable Long id) {
        return ApiResponse.ok(gameService.get(id));
    }

    @PreAuthorize("hasRole('ADMIN')")
    @PostMapping
    public ApiResponse<Game> create(@RequestBody Game game) {
        return ApiResponse.ok(gameService.create(game));
    }

    @PreAuthorize("hasRole('ADMIN')")
    @PostMapping("/{id}/versions")
    public ApiResponse<Game> bumpVersion(@PathVariable Long id, @RequestBody VersionBumpRequest req) {
        return ApiResponse.ok(gameService.updateCurrentVersion(id, req.versionNumber(), req.patchNotes()));
    }

    public record VersionBumpRequest(String versionNumber, String patchNotes) {}
}
