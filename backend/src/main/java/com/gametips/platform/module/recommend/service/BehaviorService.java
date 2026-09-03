package com.gametips.platform.module.recommend.service;

import com.gametips.platform.module.recommend.domain.UserBehaviorLog;
import com.gametips.platform.module.recommend.dto.BehaviorEvent;
import com.gametips.platform.module.recommend.repository.UserBehaviorLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class BehaviorService {

    private final UserBehaviorLogRepository behaviorRepository;

    @Transactional
    public void record(BehaviorEvent event) {
        UserBehaviorLog log = new UserBehaviorLog();
        log.setUserId(event.userId());
        log.setActionType(event.actionType());
        log.setTargetType(event.targetType());
        log.setTargetId(event.targetId());
        log.setContext(event.context());
        behaviorRepository.save(log);
    }

    @Transactional
    public void recordBatch(List<BehaviorEvent> events) {
        events.forEach(this::record);
    }

    public List<UserBehaviorLog> recent(Long userId) {
        return behaviorRepository.findTop100ByUserIdOrderByCreatedAtDesc(userId);
    }
}
