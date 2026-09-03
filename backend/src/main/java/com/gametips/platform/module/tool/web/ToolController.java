package com.gametips.platform.module.tool.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.module.tool.domain.BuildSimulator;
import com.gametips.platform.module.tool.domain.InteractiveMap;
import com.gametips.platform.module.tool.service.ToolService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/tools")
@RequiredArgsConstructor
public class ToolController {

    private final ToolService toolService;

    // ---------- 互动地图 ----------

    @GetMapping("/maps/{id}")
    public ApiResponse<InteractiveMap> getMap(@PathVariable Long id) {
        return ApiResponse.ok(toolService.getMap(id));
    }

    @GetMapping("/maps")
    public ApiResponse<List<InteractiveMap>> mapsByGame(@RequestParam Long gameId) {
        return ApiResponse.ok(toolService.mapsByGame(gameId));
    }

    @PostMapping("/maps/{id}/markers")
    public ApiResponse<InteractiveMap> addMarker(@PathVariable Long id,
                                                 @RequestBody Map<String, Object> marker) {
        return ApiResponse.ok(toolService.addMarker(id, marker));
    }

    @DeleteMapping("/maps/{id}/markers/{markerId}")
    public ApiResponse<InteractiveMap> removeMarker(@PathVariable Long id,
                                                    @PathVariable String markerId) {
        return ApiResponse.ok(toolService.removeMarker(id, markerId));
    }

    // ---------- Build 模拟器 ----------

    @GetMapping("/simulators/{id}")
    public ApiResponse<BuildSimulator> getSimulator(@PathVariable Long id) {
        return ApiResponse.ok(toolService.getSimulator(id));
    }

    @GetMapping("/simulators")
    public ApiResponse<List<BuildSimulator>> simulatorsByGame(@RequestParam Long gameId) {
        return ApiResponse.ok(toolService.simulatorsByGame(gameId));
    }

    @PostMapping("/simulators/{id}/calculate")
    public ApiResponse<Map<String, Object>> calculate(@PathVariable Long id,
                                                      @RequestBody Map<String, Object> payload) {
        return ApiResponse.ok(toolService.calculate(id, payload));
    }
}
