package com.gametips.platform.module.ai.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.ai.service.llm.LlmClient;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.version.domain.Game;
import com.gametips.platform.module.version.repository.GameRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * AI 图文攻略批量生成：
 * 为指定游戏按不同主题调用大模型生成结构化图文攻略草稿（DRAFT）。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AiGuideGenService {

    /** 每个游戏的默认攻略主题（可覆盖不同玩法维度）。 */
    private static final List<String> TOPICS = List.of(
            "新手入门、基础操作与开局要点",
            "装备/角色养成路线与资源规划",
            "核心玩法技巧与进阶操作",
            "重要系统与界面功能详解",
            "常见难点突破与 BOSS 打法",
            "每日必做、周常任务与收益最大化",
            "版本活动玩法与奖励指南",
            "配装/构筑思路与流派推荐");

    private final LlmClient llmClient;
    private final GuideRepository guideRepository;
    private final GameRepository gameRepository;

    /**
     * 为指定游戏生成 count 条图文攻略草稿（自动轮换主题）。
     * @param gameId 游戏 id
     * @param count  生成条数（默认 10，最多 20）
     * @param authorId 作者（当前用户）
     * @return 生成的攻略列表
     */
    public List<Guide> generateForGame(Long gameId, int count, Long authorId) {
        Game game = gameRepository.findById(gameId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "游戏不存在"));

        int n = Math.min(Math.max(count, 1), 20);
        List<Guide> result = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            String topic = TOPICS.get(i % TOPICS.size());
            Guide g = generateOne(game, topic, i + 1, authorId);
            result.add(g);
        }
        log.info("[ai-guide-gen] game={} 生成 {} 条图文攻略", game.getName(), result.size());
        return result;
    }

    /** 可用的攻略主题（UTC 用于批次轮换）。 */
    public List<String> topics() {
        return TOPICS;
    }

    /**
     * 为指定游戏按指定主题生成 1 条图文攻略草稿（批次任务逐条轮换主题用）。
     */
    public Guide generateByTopic(Long gameId, String topic, Long authorId) {
        Game game = gameRepository.findById(gameId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "游戏不存在"));
        return generateOne(game, topic, 1, authorId);
    }

    private Guide generateOne(Game game, String topic, int seq, Long authorId) {
        String subject = game.getName() + "：" + topic;
        try {
            Map<String, Object> raw = llmClient.generateDraft(subject);
            Guide guide = new Guide();
            guide.setGameId(game.getId());
            guide.setTitle(fixTitle(raw, game.getName(), topic));
            guide.setSummary(textOf(raw.get("summary"), 200));
            guide.setTags(List.of(game.getName(), "AI图文"));
            guide.setDifficulty(seq % 3 == 0 ? "HARD" : (seq % 2 == 0 ? "NORMAL" : "EASY"));
            guide.setType("AI_GENERATED");
            guide.setStatus(GuideStatus.DRAFT);
            guide.setAuthorId(authorId);
            guide.setContent(buildContent(raw));
            return guideRepository.save(guide);
        } catch (Exception e) {
            log.warn("[ai-guide-gen] 生成失败跳过: {} - {}", subject, e.getMessage());
            throw new BizException(ErrorCodes.INTERNAL_ERROR, "AI 生成失败: " + e.getMessage());
        }
    }

    private String fixTitle(Map<String, Object> raw, String gameName, String topic) {
        Object t = raw.get("title");
        String s = t == null ? "" : t.toString().trim();
        if (s.isBlank()) return gameName + " " + topic;
        // 标题避免过长，且附上游戏名便于列表识别
        if (!s.contains(gameName)) {
            s = gameName + " " + s;
        }
        return s.length() > 60 ? s.substring(0, 60) : s;
    }

    private String textOf(Object v, int maxLen) {
        if (v == null) return "";
        String s = v.toString().trim();
        return s.length() > maxLen ? s.substring(0, maxLen) : s;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> buildContent(Map<String, Object> raw) {
        List<Map<String, Object>> steps = new ArrayList<>();
        Object stepsObj = raw.get("steps");
        if (stepsObj instanceof List<?> list) {
            int idx = 1;
            for (Object o : list) {
                if (!(o instanceof Map<?, ?> m)) continue;
                steps.add(Map.of(
                        "step_id", idx++,
                        "title", nvl(m.get("title"), "步骤"),
                        "description", nvl(m.get("description"), ""),
                        "tips", nvl(m.get("tips"), ""),
                        "images", List.of()));
            }
        }
        if (steps.isEmpty()) {
            steps.add(Map.of(
                    "step_id", 1,
                    "title", nvl(raw.get("title"), "攻略"),
                    "description", nvl(raw.get("summary"), ""),
                    "tips", "",
                    "images", List.of()));
        }
        return Map.of("schema_version", "1.0", "steps", steps);
    }

    private String nvl(Object v, String def) {
        return v == null || v.toString().isBlank() ? def : v.toString();
    }
}