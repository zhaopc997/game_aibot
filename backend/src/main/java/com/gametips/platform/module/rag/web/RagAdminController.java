package com.gametips.platform.module.rag.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.rag.indexer.IndexerService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * RAG 管理端点(V2 §5.2 / §7.3)。
 *
 * - POST /api/v1/rag/reindex  重建 ES 索引(全量灌库)
 *
 * 生产应仅 ADMIN 可访问;骨架阶段为方便联调对所有登录用户开放。
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/rag")
@RequiredArgsConstructor
public class RagAdminController {

    private final IndexerService indexerService;

    @PostMapping("/reindex")
    public ApiResponse<Map<String, Object>> reindex() {
        // 骨架阶段:匿名也允许触发(后续改 .authenticated())
        log.info("[rag-admin] 触发全量重建索引");
        int count = indexerService.rebuildAll();
        return ApiResponse.ok(Map.of(
                "indexed", count,
                "message", "索引重建完成"
        ));
    }
}
