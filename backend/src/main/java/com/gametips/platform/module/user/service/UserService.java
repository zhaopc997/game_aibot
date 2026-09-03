package com.gametips.platform.module.user.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.user.domain.Role;
import com.gametips.platform.module.user.domain.User;
import com.gametips.platform.module.user.domain.UserRole;
import com.gametips.platform.module.user.domain.UserStatus;
import com.gametips.platform.module.user.dto.RegisterRequest;
import com.gametips.platform.module.user.repository.UserRepository;
import com.gametips.platform.module.user.repository.UserRoleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final UserRoleRepository userRoleRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public User register(RegisterRequest req) {
        if (userRepository.existsByUsername(req.username())) {
            throw new BizException(ErrorCodes.CONFLICT, "用户名已存在");
        }
        if (userRepository.existsByEmail(req.email())) {
            throw new BizException(ErrorCodes.CONFLICT, "邮箱已注册");
        }
        User user = new User();
        user.setUsername(req.username());
        user.setEmail(req.email());
        user.setPasswordHash(passwordEncoder.encode(req.password()));
        user.setStatus(UserStatus.NORMAL);
        user = userRepository.save(user);
        userRoleRepository.save(new UserRole(user.getId(), Role.USER));
        return user;
    }

    @org.springframework.cache.annotation.Cacheable(cacheNames = "user:info", key = "#userId")
    public User getById(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "用户不存在"));
    }

    public User getByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new BizException(ErrorCodes.UNAUTHORIZED, "用户名或密码错误"));
    }

    public List<String> getRoles(Long userId) {
        return userRoleRepository.findByUserId(userId).stream()
                .map(UserRole::getRole)
                .map(Enum::name)
                .toList();
    }
}
