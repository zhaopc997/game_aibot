package com.gametips.platform.module.rag.tool;

import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.rag.dto.RagHit;
import com.gametips.platform.module.rag.dto.RagQuery;
import com.gametips.platform.module.rag.service.RagService;
import com.gametips.platform.module.tool.annotation.RiskLevel;
import com.gametips.platform.module.tool.annotation.Tool;
import com.gametips.platform.module.tool.annotation.ToolParam;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * 内置 Tool 集合：攻略检索与版本兼容性校验(V2 architecture §4.3 表 #1/#2)。
 *
 * <p>接入 LLM function-calling 后，本类中标注 {@code @Tool} 的方法会自动出现在 LLM 的工具列表。
 */
@Component
@RequiredArgsConstructor
public class GuideSearchTools {

    private final RagService ragService;
    private final GuideRepository guideRepository;

    @Tool(
        name = "search_guides",
        description = "根据用户问题搜索相关游戏攻略片段。返回按相关度排序的命中列表,每条含标题、版本、原文摘要和详情 URL。",
        riskLevel = RiskLevel.READ_ONLY
    )
    public List<RagHit> searchGuides(
            @ToolParam(name = "query", description = "用户的检索问题原文,例如 '钟离圣遗物怎么刷'", required = true) String query,
            @ToolParam(name = "game_id", description = "游戏 ID,如 2", required = false) String gameId,
            @ToolParam(name = "version_id", description = "目标游戏版本 ID,缺省查最新", required = false) String versionId
    ) {
        return ragService.retrieve(RagQuery.builder()
                .query(query)
                .gameId(gameId)
                .versionId(versionId)
                .topK(5)
                .build());
    }

    /**
     * 第二个内置 Tool：查询攻略版本兼容性(§4.3 表 #2)。
     *
     * <p>真实判定规则（读 guide.status 与 guide.version_id）：
     * <ul>
     *   <li>攻略不存在 → {@code NOT_FOUND}</li>
     *   <li>状态为 OUTDATED / ARCHIVED / REJECTED → {@code OUTDATED}（已失效，需提示用户）</li>
     *   <li>状态为 DRAFT / PENDING_REVIEW → {@code UNPUBLISHED}（尚未发布，不能当作可靠依据）</li>
     *   <li>已发布且未绑定版本，或版本号一致 → {@code COMPATIBLE}</li>
     *   <li>已发布但绑定了与目标不同的版本 → {@code VERSION_MISMATCH}</li>
     * </ul>
     *
     * <p>无法判定时返回 {@code UNKNOWN}，不再一律返回 COMPATIBLE——假成功会让用户
     * 拿到过期攻略而不自知。
     */
    @Tool(
        name = "check_compatibility",
        description = "检查指定攻略列表对目标游戏版本的兼容性。返回每篇攻略的状态"
                + "(COMPATIBLE / VERSION_MISMATCH / OUTDATED / UNPUBLISHED / NOT_FOUND / UNKNOWN)。",
        riskLevel = RiskLevel.READ_ONLY
    )
    public List<Map<String, Object>> checkCompatibility(
            @ToolParam(name = "guide_ids", description = "攻略 ID 列表", required = true) List<Long> guideIds,
            @ToolParam(name = "version_id", description = "目标游戏版本 ID(数字)。可省略——省略时只判定攻略自身状态(是否 OUTDATED / 未发布)", required = false) String versionId
    ) {
        if (guideIds == null || guideIds.isEmpty()) {
            return List.of();
        }
        Long targetVersionId = parseLongOrNull(versionId);

        List<Map<String, Object>> out = new ArrayList<>(guideIds.size());
        for (Long id : guideIds) {
            out.add(evaluateOne(id, targetVersionId));
        }
        return out;
    }

    private Map<String, Object> evaluateOne(Long guideId, Long targetVersionId) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("guide_id", guideId);
        row.put("version_id", targetVersionId);

        if (guideId == null) {
            row.put("status", "UNKNOWN");
            row.put("note", "缺少攻略 ID，无法判定兼容性");
            return row;
        }

        Optional<Guide> found;
        try {
            found = guideRepository.findById(guideId);
        } catch (Exception e) {
            row.put("status", "UNKNOWN");
            row.put("note", "查询攻略状态失败: " + e.getMessage());
            return row;
        }

        if (found.isEmpty()) {
            row.put("status", "NOT_FOUND");
            row.put("note", "攻略不存在或已被删除");
            return row;
        }

        Guide guide = found.get();
        row.put("guide_status", guide.getStatus() == null ? null : guide.getStatus().name());
        row.put("guide_version_id", guide.getVersionId());

        GuideStatus status = guide.getStatus();
        if (status == GuideStatus.OUTDATED || status == GuideStatus.ARCHIVED || status == GuideStatus.REJECTED) {
            row.put("status", "OUTDATED");
            row.put("note", "攻略状态为 " + status + "，内容已失效，建议提示用户核对最新版本");
            return row;
        }
        if (status == GuideStatus.DRAFT || status == GuideStatus.PENDING_REVIEW) {
            row.put("status", "UNPUBLISHED");
            row.put("note", "攻略尚未发布（" + status + "），不应作为可靠依据");
            return row;
        }
        if (status != GuideStatus.PUBLISHED && status != GuideStatus.PENDING_VERIFICATION) {
            row.put("status", "UNKNOWN");
            row.put("note", "攻略状态 " + status + " 无明确兼容语义");
            return row;
        }

        // 已发布：比对版本
        if (targetVersionId == null || guide.getVersionId() == null) {
            row.put("status", "COMPATIBLE");
            row.put("note", "未指定目标版本或攻略未绑定版本，按最新内容处理");
            return row;
        }
        if (targetVersionId.equals(guide.getVersionId())) {
            row.put("status", "COMPATIBLE");
            row.put("note", "攻略绑定的版本与目标版本一致");
            return row;
        }
        row.put("status", "VERSION_MISMATCH");
        row.put("note", "攻略版本 " + guide.getVersionId()
                + " 与目标版本 " + targetVersionId + " 不一致，可能已过期");
        return row;
    }

    private static Long parseLongOrNull(String s) {
        if (s == null || s.isBlank()) return null;
        try {
            return Long.parseLong(s.trim());
        } catch (NumberFormatException e) {
            return null;
        }
    }
}