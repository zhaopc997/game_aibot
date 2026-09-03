package com.gametips.platform.module.notification.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.notification.domain.Notification;
import com.gametips.platform.module.notification.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/notifications")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    @GetMapping
    public ApiResponse<List<Notification>> list() {
        return ApiResponse.ok(notificationService.list(CurrentUser.userId()));
    }

    @PostMapping("/read")
    public ApiResponse<Void> markRead() {
        notificationService.markAllRead(CurrentUser.userId());
        return ApiResponse.ok();
    }
}
