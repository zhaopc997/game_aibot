package com.gametips.platform.module.notification.listener;

import com.gametips.platform.module.notification.service.NotificationCreatedEvent;
import com.gametips.platform.module.notification.service.NotificationService;
import com.gametips.platform.module.review.event.GuideReviewFinishedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

/**
 * 监听通知创建并 WebSocket 推送，同时监听业务领域事件生成站内信。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class NotificationPushListener {

    private final SimpMessagingTemplate messagingTemplate;
    private final NotificationService notificationService;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onNotificationCreated(NotificationCreatedEvent event) {
        Long userId = event.notification().getUserId();
        messagingTemplate.convertAndSendToUser(
                String.valueOf(userId), "/queue/notifications", event.notification());
        log.debug("pushed notification to user {}", userId);
    }

    @EventListener
    public void onGuideReviewFinished(GuideReviewFinishedEvent event) {
        if (event.getAuthorId() == null || event.getAuthorId() <= 0) return;
        String title = event.isPassed() ? "攻略审核通过" : "攻略未通过审核";
        String content = event.isPassed()
                ? "恭喜！你的攻略《" + event.getGuideTitle() + "》已通过审核并发布。"
                : "抱歉，你的攻略《" + event.getGuideTitle() + "》未通过审核。" + (event.getReason() != null ? " 原因：" + event.getReason() : "");
        notificationService.create(event.getAuthorId(), "GUIDE_AUDIT", title, content, "guide", event.getGuideId());
        log.info("[notification] 审核结果通知已发往用户 id={}", event.getAuthorId());
    }
}
