package com.gametips.platform.module.memory.service;

import com.gametips.platform.module.memory.dto.ConversationMessage;
import com.gametips.platform.module.memory.dto.PlayerPreference;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 内存版 Memory 实现(§12 第 1 条:骨架阶段全部 mock,不接 Redis/PG)。
 *
 * <p>短期记忆用 {@link ConcurrentHashMap} 存每个会话的 List;
 * 真实场景下短期记忆走 Redis(Long add,Trim trim,Expire 30min),
 * 长期偏好走 PG user_game_profile.preference JSONB。
 *
 * <p>线程安全:ConcurrentHashMap + List 内部用 synchronized 块保护。
 * 生产实现需要替换为 Redis-backed 版本。
 */
@Slf4j
@Service
public class InMemoryMemoryService implements MemoryService, PreferenceService {

    /** 滑动窗口大小;真实场景从配置注入 */
    private static final int SHORT_WINDOW = 10;

    private final Map<UUID, List<ConversationMessage>> shortStore = new ConcurrentHashMap<>();
    private final Map<Long, PlayerPreference> longStore = new ConcurrentHashMap<>();

    // ─── 短期记忆 ──────────────────────────────────────

    @Override
    public synchronized List<ConversationMessage> shortTerm(UUID conversationId, ConversationMessage message) {
        List<ConversationMessage> list = shortStore.computeIfAbsent(conversationId, k -> new ArrayList<>());
        list.add(message);
        // 滑动窗口:只保留最近 SHORT_WINDOW 条
        while (list.size() > SHORT_WINDOW) {
            list.remove(0);
        }
        log.debug("[memory] shortTerm conv={} size={}", conversationId, list.size());
        return new ArrayList<>(list);
    }

    @Override
    public List<ConversationMessage> readShort(UUID conversationId) {
        List<ConversationMessage> list = shortStore.get(conversationId);
        if (list == null) return Collections.emptyList();
        synchronized (list) {
            return new ArrayList<>(list);
        }
    }

    @Override
    public synchronized void clearShort(UUID conversationId) {
        shortStore.remove(conversationId);
        log.info("[memory] clearShort conv={}", conversationId);
    }

    // ─── 长期偏好 ──────────────────────────────────────

    @Override
    public PlayerPreference loadPreference(Long userId) {
        return longStore.getOrDefault(userId, PlayerPreference.builder().build());
    }

    @Override
    public void savePreference(Long userId, PlayerPreference pref) {
        longStore.put(userId, pref);
        log.info("[memory] savePreference user={} pref={}", userId, pref);
    }

    // PreferenceService 别名(便于以后单独切实现)
    @Override
    public PlayerPreference load(Long userId) {
        return loadPreference(userId);
    }

    @Override
    public void save(Long userId, PlayerPreference pref) {
        savePreference(userId, pref);
    }
}
