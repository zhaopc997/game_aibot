package com.gametips.platform.module.memory.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gametips.platform.module.memory.dto.ConversationMessage;
import com.gametips.platform.module.memory.dto.PlayerPreference;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Primary;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 基于 Redis 的分布式会话短期记忆与玩家偏好服务。
 * <ul>
 *   <li>短期记忆：Redis List 滑动窗口（最近 10 条）+ 30 分钟 TTL 自动过期淘汰，杜绝内存泄漏</li>
 *   <li>长期偏好：Redis String (JSON) 持久化（30 天 TTL）</li>
 *   <li>弹性容灾：Redis 故障时自动降级到本地内存缓存，确保主干对话流程不中断</li>
 * </ul>
 */
@Slf4j
@Service
@Primary
@RequiredArgsConstructor
public class RedisMemoryService implements MemoryService, PreferenceService {

    private static final int SHORT_WINDOW = 10;
    private static final Duration CONV_TTL = Duration.ofMinutes(30);
    private static final Duration PREF_TTL = Duration.ofDays(30);

    private static final String CONV_KEY_PREFIX = "agent:conv:";
    private static final String PREF_KEY_PREFIX = "agent:pref:user:";

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    // 本地降级备用存储
    private final Map<UUID, List<ConversationMessage>> localShortFallback = new ConcurrentHashMap<>();
    private final Map<Long, PlayerPreference> localPrefFallback = new ConcurrentHashMap<>();

    @Override
    public List<ConversationMessage> shortTerm(UUID conversationId, ConversationMessage message) {
        if (conversationId == null || message == null) {
            return Collections.emptyList();
        }
        String key = CONV_KEY_PREFIX + conversationId;
        try {
            String json = objectMapper.writeValueAsString(message);
            redisTemplate.opsForList().rightPush(key, json);
            redisTemplate.opsForList().trim(key, -SHORT_WINDOW, -1);
            redisTemplate.expire(key, CONV_TTL);
            log.debug("[memory:redis] appended convId={} role={}", conversationId, message.getRole());
            return readShort(conversationId);
        } catch (Exception e) {
            log.warn("[memory:redis] redis shortTerm write error convId={}, falling back to local: {}",
                    conversationId, e.getMessage());
            return localShortTerm(conversationId, message);
        }
    }

    @Override
    public List<ConversationMessage> readShort(UUID conversationId) {
        if (conversationId == null) {
            return Collections.emptyList();
        }
        String key = CONV_KEY_PREFIX + conversationId;
        try {
            List<String> rawList = redisTemplate.opsForList().range(key, 0, -1);
            if (rawList == null || rawList.isEmpty()) {
                return localShortFallback.getOrDefault(conversationId, Collections.emptyList());
            }
            List<ConversationMessage> messages = new ArrayList<>(rawList.size());
            for (String raw : rawList) {
                try {
                    messages.add(objectMapper.readValue(raw, ConversationMessage.class));
                } catch (JsonProcessingException ex) {
                    log.error("[memory:redis] deserialize message failed, json={}", raw, ex);
                }
            }
            return messages;
        } catch (Exception e) {
            log.warn("[memory:redis] redis readShort error convId={}, reading local fallback: {}",
                    conversationId, e.getMessage());
            return localShortFallback.getOrDefault(conversationId, Collections.emptyList());
        }
    }

    @Override
    public void clearShort(UUID conversationId) {
        if (conversationId == null) {
            return;
        }
        String key = CONV_KEY_PREFIX + conversationId;
        try {
            redisTemplate.delete(key);
            log.info("[memory:redis] cleared convId={}", conversationId);
        } catch (Exception e) {
            log.warn("[memory:redis] redis clearShort error convId={}: {}", conversationId, e.getMessage());
        }
        localShortFallback.remove(conversationId);
    }

    @Override
    public PlayerPreference loadPreference(Long userId) {
        if (userId == null || userId <= 0) {
            return PlayerPreference.builder().build();
        }
        String key = PREF_KEY_PREFIX + userId;
        try {
            String json = redisTemplate.opsForValue().get(key);
            if (json != null && !json.isBlank()) {
                return objectMapper.readValue(json, PlayerPreference.class);
            }
        } catch (Exception e) {
            log.warn("[memory:redis] redis loadPreference error userId={}: {}", userId, e.getMessage());
        }
        return localPrefFallback.getOrDefault(userId, PlayerPreference.builder().build());
    }

    @Override
    public void savePreference(Long userId, PlayerPreference pref) {
        if (userId == null || userId <= 0 || pref == null) {
            return;
        }
        String key = PREF_KEY_PREFIX + userId;
        try {
            String json = objectMapper.writeValueAsString(pref);
            redisTemplate.opsForValue().set(key, json, PREF_TTL);
            log.info("[memory:redis] saved pref userId={}", userId);
        } catch (Exception e) {
            log.warn("[memory:redis] redis savePreference error userId={}: {}", userId, e.getMessage());
            localPrefFallback.put(userId, pref);
        }
    }

    @Override
    public PlayerPreference load(Long userId) {
        return loadPreference(userId);
    }

    @Override
    public void save(Long userId, PlayerPreference pref) {
        savePreference(userId, pref);
    }

    private List<ConversationMessage> localShortTerm(UUID conversationId, ConversationMessage message) {
        List<ConversationMessage> list = localShortFallback.computeIfAbsent(conversationId, k -> new ArrayList<>());
        synchronized (list) {
            list.add(message);
            while (list.size() > SHORT_WINDOW) {
                list.remove(0);
            }
            return new ArrayList<>(list);
        }
    }
}
