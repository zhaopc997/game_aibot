package com.gametips.platform.module.rag.tool;

import com.gametips.platform.module.rag.dto.RagHit;
import com.gametips.platform.module.rag.dto.RagQuery;
import com.gametips.platform.module.rag.service.RagService;
import com.gametips.platform.module.tool.annotation.RiskLevel;
import com.gametips.platform.module.tool.annotation.Tool;
import com.gametips.platform.module.tool.annotation.ToolParam;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

/**
 * 第一个内置 Tool:搜索攻略(V2 architecture §4.3 表 #1)。
 *
 * <p>骨架阶段:LlmService / AgentService 直接调它,不需要走 LLM 的 function-calling;
 * 接 LangChain4j 后该方法会自动出现在 LLM 的工具列表。
 */
@Component
@RequiredArgsConstructor
public class GuideSearchTools {

    private final RagService ragService;

    @Tool(
        name = "search_guides",
        description = "根据用户问题搜索相关游戏攻略片段。返回按相关度排序的命中列表,每条含标题、版本、原文摘要和详情 URL。",
        riskLevel = RiskLevel.READ_ONLY
    )
    public List<RagHit> searchGuides(
            @ToolParam(name = "query", description = "用户的检索问题原文,例如 '钟离圣遗物怎么刷'", required = true) String query,
            @ToolParam(name = "game_id", description = "游戏 ID,如 yuanshen / starrail", required = false) String gameId,
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
     * 第二个内置 Tool:查询攻略版本兼容性(§4.3 表 #2)。
     * 骨架阶段:所有攻略都视为兼容(V2 接 content 模块的真实状态机)。
     */
    @Tool(
        name = "check_compatibility",
        description = "检查指定攻略列表对目标游戏版本的兼容性。返回每篇攻略的兼容状态(COMPATIBLE / OUTDATED / UNKNOWN)。",
        riskLevel = RiskLevel.READ_ONLY
    )
    public List<Map<String, Object>> checkCompatibility(
            @ToolParam(name = "guide_ids", description = "攻略 ID 列表", required = true) List<Long> guideIds,
            @ToolParam(name = "version_id", description = "目标游戏版本 ID", required = true) String versionId
    ) {
        return guideIds.stream()
                .map(id -> Map.<String, Object>of(
                        "guide_id", id,
                        "version_id", versionId,
                        "status", "COMPATIBLE",
                        "note", "mock 阶段一律视为兼容;真实实现读 guide.status + game_version"
                ))
                .toList();
    }
}
