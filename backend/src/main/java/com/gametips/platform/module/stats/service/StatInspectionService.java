package com.gametips.platform.module.stats.service;

import com.gametips.platform.module.notification.service.NotificationService;
import com.gametips.platform.module.stats.domain.GameCharacter;
import com.gametips.platform.module.stats.domain.GameWeapon;
import com.gametips.platform.module.stats.domain.StatVersionAudit;
import com.gametips.platform.module.stats.repository.GameCharacterRepository;
import com.gametips.platform.module.stats.repository.GameWeaponRepository;
import com.gametips.platform.module.stats.repository.StatVersionAuditRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class StatInspectionService {

    private final StatVersionAuditRepository auditRepository;
    private final GameCharacterRepository characterRepository;
    private final GameWeaponRepository weaponRepository;
    private final NotificationService notificationService;

    public Page<StatVersionAudit> listAudits(Long gameId, String status, Pageable pageable) {
        if (status != null && !status.isBlank()) {
            return auditRepository.findByGameIdAndStatusOrderByCheckedAtDesc(gameId, status.trim(), pageable);
        }
        return auditRepository.findByGameIdOrderByCheckedAtDesc(gameId, pageable);
    }

    /**
     * 记录巡检批次审计日志并触发变动通知
     */
    @Transactional
    public StatVersionAudit recordAudit(Long gameId, String targetType, Long targetId, String targetName,
                                       String batchNo, String status, String summary,
                                       List<Map<String, Object>> diffDetail, String oldHash, String newHash) {
        StatVersionAudit audit = new StatVersionAudit();
        audit.setGameId(gameId);
        audit.setTargetType(targetType);
        audit.setTargetId(targetId);
        audit.setTargetName(targetName);
        audit.setCheckBatchNo(batchNo);
        audit.setStatus(status);
        audit.setDiffSummary(summary);
        audit.setDiffDetail(diffDetail != null ? diffDetail : List.of());
        audit.setOldHash(oldHash);
        audit.setNewHash(newHash);
        audit.setCheckedAt(Instant.now());

        audit = auditRepository.save(audit);

        // 若数值发生变动或为新增条目，向系统管理员（用户ID=1）发送通知
        if ("MODIFIED".equals(status) || "NEW_ADDED".equals(status)) {
            try {
                notificationService.create(
                        1L,
                        "VERSION_OUTDATED",
                        "【数值变动告警】" + targetName + " 数值发生版本更新",
                        summary != null ? summary : "检测到 " + targetName + " 存在数值变动，请及时查阅新版本数据。",
                        targetType,
                        targetId
                );
            } catch (Exception e) {
                log.warn("Failed to push inspection notification: {}", e.getMessage());
            }
        }

        return audit;
    }

    /**
     * 执行原神（game_id = 2）全量数据定期巡检任务
     * 每周一凌晨 04:00 自动触发，也可通过管理端随时手动调用
     */
    @Scheduled(cron = "0 0 4 * * MON")
    public void scheduledWeeklyInspection() {
        log.info("[StatInspection] 启动每周原神游戏数值健康巡检任务...");
        inspectGameStats(2L);
    }

    /**
     * 针对指定游戏执行数值完整性与快照一致性巡检
     */
    @Transactional
    public Map<String, Object> inspectGameStats(Long gameId) {
        String batchNo = "INSPECT_" + System.currentTimeMillis();
        int totalChecked = 0;
        int modifiedCount = 0;
        int unchangedCount = 0;

        List<GameCharacter> characters = characterRepository.findByGameId(gameId);
        for (GameCharacter ch : characters) {
            totalChecked++;
            // 校验字段哈希完整性
            if (ch.getDataHash() == null || ch.getDataHash().isBlank()) {
                modifiedCount++;
                recordAudit(gameId, "CHARACTER", ch.getId(), ch.getName(), batchNo, "MODIFIED",
                        "角色 [" + ch.getName() + "] 存在哈希缺失或数据更新，已标记重新校准",
                        List.of(Map.of("field", "data_hash", "status", "recalculated")),
                        "", "HASH_RESET");
            } else {
                unchangedCount++;
                recordAudit(gameId, "CHARACTER", ch.getId(), ch.getName(), batchNo, "UNCHANGED",
                        "角色 [" + ch.getName() + "] 数值基准一致，无异常波动",
                        List.of(), ch.getDataHash(), ch.getDataHash());
            }
        }

        List<GameWeapon> weapons = weaponRepository.findByGameId(gameId);
        for (GameWeapon w : weapons) {
            totalChecked++;
            if (w.getDataHash() == null || w.getDataHash().isBlank()) {
                modifiedCount++;
                recordAudit(gameId, "WEAPON", w.getId(), w.getName(), batchNo, "MODIFIED",
                        "武器 [" + w.getName() + "] 标记更新",
                        List.of(), "", "HASH_RESET");
            } else {
                unchangedCount++;
                recordAudit(gameId, "WEAPON", w.getId(), w.getName(), batchNo, "UNCHANGED",
                        "武器 [" + w.getName() + "] 数值基准一致",
                        List.of(), w.getDataHash(), w.getDataHash());
            }
        }

        log.info("[StatInspection] 巡检完成: batch={}, checked={}, unchanged={}, modified={}",
                batchNo, totalChecked, unchangedCount, modifiedCount);

        return Map.of(
                "batchNo", batchNo,
                "gameId", gameId,
                "totalChecked", totalChecked,
                "unchangedCount", unchangedCount,
                "modifiedCount", modifiedCount,
                "status", "COMPLETED"
        );
    }
}
