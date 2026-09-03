package com.gametips.platform.module.notification.service;

import com.gametips.platform.module.notification.domain.Notification;

/**
 * 通知创建事件（事务提交后推送 WebSocket）。
 */
public record NotificationCreatedEvent(Notification notification) {}
