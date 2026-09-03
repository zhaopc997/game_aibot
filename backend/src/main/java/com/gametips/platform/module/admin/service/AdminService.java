package com.gametips.platform.module.admin.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.user.domain.User;
import com.gametips.platform.module.user.domain.UserStatus;
import com.gametips.platform.module.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AdminService {

    private final UserRepository userRepository;

    public Page<User> listUsers(int page, int size) {
        return userRepository.findAll(PageRequest.of(page, size));
    }

    @Transactional
    public User changeUserStatus(Long userId, String status) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "用户不存在"));
        user.setStatus(UserStatus.valueOf(status));
        return userRepository.save(user);
    }
}
