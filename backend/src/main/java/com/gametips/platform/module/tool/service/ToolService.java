package com.gametips.platform.module.tool.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.tool.domain.BuildSimulator;
import com.gametips.platform.module.tool.domain.InteractiveMap;
import com.gametips.platform.module.tool.repository.BuildSimulatorRepository;
import com.gametips.platform.module.tool.repository.InteractiveMapRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 工具服务：互动地图标记管理、Build 模拟器计算。
 */
@Service
@RequiredArgsConstructor
public class ToolService {

    private final InteractiveMapRepository mapRepository;
    private final BuildSimulatorRepository simulatorRepository;

    // ---------- 互动地图 ----------

    public InteractiveMap getMap(Long id) {
        return mapRepository.findById(id)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "地图不存在"));
    }

    public List<InteractiveMap> mapsByGame(Long gameId) {
        return mapRepository.findByGameId(gameId);
    }

    /**
     * 添加个人标记：给 marker 生成 id 并入列表。
     */
    @Transactional
    public InteractiveMap addMarker(Long mapId, Map<String, Object> marker) {
        InteractiveMap map = getMap(mapId);
        List<Map<String, Object>> markers = new ArrayList<>(map.getMarkers());
        marker.put("id", UUID.randomUUID().toString());
        markers.add(marker);
        map.setMarkers(markers);
        return mapRepository.save(map);
    }

    /**
     * 删除标记：按 marker.id 移除。
     */
    @Transactional
    public InteractiveMap removeMarker(Long mapId, String markerId) {
        InteractiveMap map = getMap(mapId);
        List<Map<String, Object>> markers = new ArrayList<>(map.getMarkers());
        markers.removeIf(m -> markerId.equals(m.get("id")));
        map.setMarkers(markers);
        return mapRepository.save(map);
    }

    // ---------- Build 模拟器 ----------

    public BuildSimulator getSimulator(Long id) {
        return simulatorRepository.findById(id)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "模拟器不存在"));
    }

    public List<BuildSimulator> simulatorsByGame(Long gameId) {
        return simulatorRepository.findByGameId(gameId);
    }

    /**
     * 执行构建计算（MVP 简单聚合）：
     * 输入 {attributes: {攻击: 100, 暴击率: 20}, bonuses: [...]}
     * 输出总属性与综合战力（占位算法，真实公式由 config 驱动）。
     */
    public Map<String, Object> calculate(Long id, Map<String, Object> payload) {
        BuildSimulator sim = getSimulator(id);
        @SuppressWarnings("unchecked")
        Map<String, Object> attrs = (Map<String, Object>) payload.getOrDefault("attributes", Map.of());
        List<?> bonuses = payload.get("bonuses") instanceof List<?> l ? l : List.of();

        double attack = num(attrs.get("攻击"));
        double critRate = num(attrs.get("暴击率"));
        double critDmg = num(attrs.get("暴击伤害"));
        double base = 100;

        // 战力 = 基础 + 攻击*系数 + 暴击期望加成
        double expectedCrit = 1 + (critRate / 100.0) * (critDmg / 100.0);
        double power = base + attack * 1.0 * expectedCrit + bonuses.size() * 5.0;

        return Map.of(
                "simulator", sim.getName(),
                "attack", attack,
                "critRate", critRate,
                "critDmg", critDmg,
                "power", Math.round(power * 100) / 100.0,
                "bonusCount", bonuses.size());
    }

    private double num(Object o) {
        if (o instanceof Number n) return n.doubleValue();
        try {
            return Double.parseDouble(String.valueOf(o));
        } catch (Exception e) {
            return 0;
        }
    }
}
