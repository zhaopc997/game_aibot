package com.gametips.platform.module.recommend.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.recommend.dto.BehaviorEvent;
import com.gametips.platform.module.recommend.service.BehaviorService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/behaviors")
@RequiredArgsConstructor
public class BehaviorController {

    private final BehaviorService behaviorService;

    @PostMapping
    public ApiResponse<Void> record(@Valid @RequestBody BehaviorEvent event) {
        behaviorService.record(withCurrentUser(event));
        return ApiResponse.ok();
    }

    @PostMapping("/batch")
    public ApiResponse<Void> recordBatch(@Valid @RequestBody List<BehaviorEvent> events) {
        behaviorService.recordBatch(events.stream().map(this::withCurrentUser).toList());
        return ApiResponse.ok();
    }

    private BehaviorEvent withCurrentUser(BehaviorEvent e) {
        return new BehaviorEvent(
                CurrentUser.userId(), e.actionType(), e.targetType(), e.targetId(), e.context());
    }
}
