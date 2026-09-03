package com.gametips.platform.module.notification.listener;

import com.gametips.platform.module.notification.service.NotificationCreatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

/**
 * 通知创建后通过 WebSocket 推送到用户队列 /user/queue/notifications。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class NotificationPushListener {

    private final SimpMessagingTemplate messagingTemplate;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onNotificationCreated(NotificationCreatedEvent event) {
        Long userId = event.notification().getUserId();
        messagingTemplate.convertAndSendToUser(
                String.valueOf(userId), "/queue/notifications", event.notification());
        log.debug("pushed notification to user {}", userId);
    }
}
