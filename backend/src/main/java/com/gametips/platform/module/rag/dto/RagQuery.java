package com.gametips.platform.module.rag.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * RAG 检索的输入(V2 architecture §4.4)。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RagQuery {

    /** 用户问题原文 */
    private String query;

    /** 游戏 ID(强过滤,无则视为跨游戏检索) */
    private String gameId;

    /** 目标版本 ID(强过滤 ±1 个版本) */
    private String versionId;

    /** 召回 Top-K */
    @Builder.Default
    private int topK = 10;
}
