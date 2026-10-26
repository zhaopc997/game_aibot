package com.gametips.platform.module.admin.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.user.domain.User;
import com.gametips.platform.module.user.domain.UserStatus;
import com.gametips.platform.module.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class AdminService {

    private static final String USER_STATUS_CACHE_PREFIX = "user:status:";

    private final UserRepository userRepository;
    private final StringRedisTemplate redisTemplate;

    public Page<User> listUsers(int page, int size) {
        return userRepository.findAll(PageRequest.of(page, size));
    }

    @Transactional
    public User changeUserStatus(Long userId, String status) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "用户不存在"));
        user.setStatus(UserStatus.valueOf(status));
        User saved = userRepository.save(user);
        try {
            redisTemplate.delete(USER_STATUS_CACHE_PREFIX + userId);
        } catch (Exception e) {
            log.warn("[admin] failed to evict user status cache for userId={}: {}", userId, e.getMessage());
        }
        return saved;
    }
}
