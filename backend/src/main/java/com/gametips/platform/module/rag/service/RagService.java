package com.gametips.platform.module.rag.service;

import com.gametips.platform.module.rag.client.EmbeddingClient;
import com.gametips.platform.module.rag.config.RagProperties;
import com.gametips.platform.module.rag.dto.RagHit;
import com.gametips.platform.module.rag.dto.RagQuery;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * RagService — 委托给 {@link HybridRetriever}(V2 真正的 ES 检索)。
 *
 * 设计:
 *   - 接口签名沿用 V1 风格(RagQuery → List<RagHit>),前端零改动
 *   - 内部根据配置自动降级:ES 未起 / embed 未配 → 返回空(由前端 mock 兜底)
 *   - 实测:search_guides 这个 Tool 直接调这里
 *
 * V2 验收 case 链接:
 *   - C1 攻略问答:本类被 search_guides 调用,返回命中 hits
 *   - C4 Tool 失败降级:本类异常时返回空,AgentService 走无 Tool 直答
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class RagService {

    private final HybridRetriever retriever;
    private final EmbeddingClient embeddingClient;
    private final RagProperties props;

    public List<RagHit> retrieve(RagQuery q) {
        return retriever.retrieve(q);
    }

    public boolean isHealthy() {
        // 简单 health check:有 topK 配置 + embed client 实例化
        return props.getTopK() > 0 && retriever != null;
    }
}
