package com.gametips.platform.module.version.listener;

import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.notification.service.NotificationService;
import com.gametips.platform.module.version.event.GameVersionUpdatedEvent;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

import java.util.List;

/**
 * 版本更新事件处理：
 * 1. 将该游戏下 PUBLISHED 攻略标记为 PENDING_VERIFICATION。
 * 2. 通知各作者版本可能已过期。
 * 宽限期：MVP 直接标记；正式环境可在标记前判断上次版本快照时间是否超过宽限期。
 */
@Component
@RequiredArgsConstructor
public class GameVersionEventListener {

    private final GuideRepository guideRepository;
    private final NotificationService notificationService;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onVersionUpdated(GameVersionUpdatedEvent event) {
        List<Guide> guides = guideRepository.findByGameIdAndStatus(
                event.gameId(), GuideStatus.PUBLISHED);
        for (Guide guide : guides) {
            guide.setStatus(GuideStatus.PENDING_VERIFICATION);
            guideRepository.save(guide);

            notificationService.create(
                    guide.getAuthorId(),
                    "VERSION_OUTDATED",
                    "攻略可能已过期",
                    "游戏已更新到 %s，你的攻略《%s》需要确认是否仍适用。"
                            .formatted(event.newVersionNumber(), guide.getTitle()),
                    "guide", guide.getId());
        }
    }
}
