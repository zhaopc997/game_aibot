package com.gametips.platform.module.notification.service;

import com.gametips.platform.module.notification.domain.Notification;
import com.gametips.platform.module.notification.repository.NotificationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 通知服务：站内信 + WebSocket 实时推送。
 * 创建通知后发布 NotificationCreatedEvent，由监听器异步推送到 WebSocket。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationRepository notificationRepository;
    private final ApplicationEventPublisher eventPublisher;

    public List<Notification> list(Long userId) {
        return notificationRepository.findTop50ByUserIdOrderByCreatedAtDesc(userId);
    }

    @Transactional
    public void markAllRead(Long userId) {
        notificationRepository.markAllRead(userId);
    }

    @Transactional
    public Notification create(Long userId, String type, String title, String content,
                               String relatedType, Long relatedId) {
        Notification n = new Notification();
        n.setUserId(userId);
        n.setType(type);
        n.setTitle(title);
        n.setContent(content);
        n.setRelatedType(relatedType);
        n.setRelatedId(relatedId);
        n.setIsRead(false);
        n = notificationRepository.save(n);
        eventPublisher.publishEvent(new NotificationCreatedEvent(n));
        return n;
    }
}
