package com.gametips.platform.module.rag.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 单个攻略 chunk 的检索命中(V2 architecture §4.4)。
 *
 * <p>真实阶段字段:embedding 向量、BM25 score、向量 score、rerank score、原文。
 * 骨架阶段只保留前端可用的展示字段。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RagHit {

    /** 攻略 ID */
    private Long guideId;

    /** 攻略标题 */
    private String title;

    /** 来源游戏 ID */
    private String gameId;

    /** 来源游戏版本 */
    private String version;

    /** 命中片段文本(原文摘要或步骤标题) */
    private String snippet;

    /** 命中片段在原文中的位置(如 step_id) */
    private String anchor;

    /** 综合相关度(0-1) */
    private double score;

    /** 攻略详情 URL(前端跳转用) */
    private String url;
}
