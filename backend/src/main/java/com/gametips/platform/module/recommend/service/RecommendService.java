package com.gametips.platform.module.recommend.service;

import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.recommend.domain.UserBehaviorLog;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;

/**
 * MVP 阶段：基于行为日志 + 标签的规则推荐，结果缓存 Redis 10 分钟。
 * 逻辑：
 *   1. 取用户最近行为，统计高频游戏与高频标签作为用户画像；
 *   2. 召回同游戏最新攻略 + 命中标签的攻略，按分数排序；
 *   3. 无画像时回退到全站最新攻略。
 * 后期引入协同过滤（Spark/Flink）。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class RecommendService {

    private static final String FEED_KEY = "recommend:feed:";
    private static final String GUIDE_KEY = "recommend:guide:";
    private static final Duration CACHE_TTL = Duration.ofMinutes(10);

    private final RedisTemplate<String, Object> redisTemplate;
    private final GuideRepository guideRepository;
    private final BehaviorService behaviorService;

    @SuppressWarnings("unchecked")
    public List<Long> feed(Long userId, int limit) {
        String key = FEED_KEY + userId;
        Object cached = redisTemplate.opsForValue().get(key);
        if (cached instanceof List<?> list && !list.isEmpty()) {
            return ((List<Object>) list).stream().limit(limit).map(o -> Long.valueOf(o.toString())).toList();
        }

        List<Long> result = computeFeed(userId, limit);
        if (!result.isEmpty()) {
            redisTemplate.opsForValue().set(key, result, CACHE_TTL);
        }
        return result;
    }

    public List<Long> recommendByGame(Long userId, Long gameId, int limit) {
        List<Guide> candidates = guideRepository
                .findTop10ByGameIdAndStatusOrderByUpdatedAtDesc(gameId, GuideStatus.PUBLISHED);
        return candidates.stream().map(Guide::getId).toList();
    }

    private List<Long> computeFeed(Long userId, int limit) {
        List<UserBehaviorLog> behaviors = behaviorService.recent(userId);
        if (behaviors.isEmpty()) {
            return guideRepository
                    .findTop3ByStatusOrderByUpdatedAtDesc(GuideStatus.PUBLISHED)
                    .stream().map(Guide::getId).toList();
        }

        // 用户画像：行为目标 gameId / tag 权重
        Map<Long, Integer> gameScore = new HashMap<>();
        Map<String, Integer> tagScore = new HashMap<>();
        Set<Long> viewedIds = new LinkedHashSet<>();
        for (UserBehaviorLog b : behaviors) {
            if ("guide".equals(b.getTargetType())) {
                viewedIds.add(b.getTargetId());
            }
            if (b.getContext() != null) {
                Object gid = b.getContext().get("gameId");
                if (gid instanceof Number n) {
                    gameScore.merge(n.longValue(), 1, Integer::sum);
                }
                Object tags = b.getContext().get("tags");
                if (tags instanceof List<?> tl) {
                    tl.forEach(t -> tagScore.merge(String.valueOf(t), 1, Integer::sum));
                }
            }
        }

        // 召回候选：最新攻略 + 按 gameId 权重排序
        List<Guide> pool = guideRepository
                .findTop3ByStatusOrderByUpdatedAtDesc(GuideStatus.PUBLISHED);
        List<Guide> candidates = new ArrayList<>(pool);
        if (!gameScore.isEmpty()) {
            Long topGame = gameScore.entrySet().stream()
                    .max(Comparator.comparingInt(Map.Entry::getValue))
                    .map(Map.Entry::getKey).orElse(null);
            if (topGame != null) {
                candidates.addAll(0, guideRepository
                        .findTop10ByGameIdAndStatusOrderByUpdatedAtDesc(topGame, GuideStatus.PUBLISHED));
            }
        }

        List<Long> result = new ArrayList<>();
        for (Guide g : candidates) {
            if (result.size() >= limit) break;
            if (viewedIds.contains(g.getId())) continue;
            result.add(g.getId());
        }
        // 兜底补充
        if (result.size() < limit) {
            for (Guide g : pool) {
                if (result.size() >= limit) break;
                if (!result.contains(g.getId())) result.add(g.getId());
            }
        }
        return result;
    }
}
