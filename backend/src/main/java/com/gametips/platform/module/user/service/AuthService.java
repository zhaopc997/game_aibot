package com.gametips.platform.module.user.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.common.security.JwtService;
import com.gametips.platform.module.user.domain.User;
import com.gametips.platform.module.user.dto.LoginRequest;
import com.gametips.platform.module.user.dto.LoginResponse;
import com.gametips.platform.module.user.dto.RefreshRequest;
import com.gametips.platform.module.user.dto.RegisterRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 认证编排：注册/登录/刷新，签发 Access + Refresh Token。
 */
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserService userService;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public LoginResponse register(RegisterRequest req) {
        User user = userService.register(req);
        List<String> roles = userService.getRoles(user.getId());
        return issueTokens(user, roles);
    }

    public LoginResponse login(LoginRequest req) {
        User user = userService.getByUsername(req.username());
        if (!passwordEncoder.matches(req.password(), user.getPasswordHash())) {
            throw new BizException(ErrorCodes.UNAUTHORIZED, "用户名或密码错误");
        }
        List<String> roles = userService.getRoles(user.getId());
        return issueTokens(user, roles);
    }

    public LoginResponse refresh(RefreshRequest req) {
        Long userId = jwtService.extractUserId(req.refreshToken());
        User user = userService.getById(userId);
        if (user.getStatus() != com.gametips.platform.module.user.domain.UserStatus.NORMAL) {
            throw new BizException(ErrorCodes.UNAUTHORIZED, "账号已被禁用");
        }
        List<String> roles = userService.getRoles(user.getId());
        return issueTokens(user, roles);
    }

    private LoginResponse issueTokens(User user, List<String> roles) {
        String access = jwtService.generateAccessToken(user.getId(), user.getUsername(), roles);
        String refresh = jwtService.generateRefreshToken(user.getId());
        return LoginResponse.of(access, refresh, jwtService.accessTokenTtlSeconds(), user, roles);
    }
}
