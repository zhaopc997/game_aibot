package com.gametips.platform.module.memory.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 玩家长期偏好(Memory.Long)。
 *
 * <p>V2 简化为 JSONB 结构(V2 architecture §4.5),不引独立向量库。
 * 字段按需扩展,本骨架阶段只列最常用。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PlayerPreference {

    /** 常玩游戏 ID 列表,如 ["yuanshen","starrail"] */
    private List<String> favoriteGames;

    /** 玩法风格:casual / hardcore / competitive / collector */
    private String playStyle;

    /** 语言偏好:zh-CN / en */
    private String languagePref;

    /** 回答详细度:concise / detailed */
    private String detailLevel;

    /** 兴趣标签:build / lore / speedrun / ... */
    private List<String> interestTags;
}
