package com.gametips.platform.module.user.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.common.security.JwtService;
import com.gametips.platform.common.security.LoginAttemptService;
import com.gametips.platform.common.security.RefreshTokenService;
import com.gametips.platform.module.user.domain.User;
import com.gametips.platform.module.user.domain.UserStatus;
import com.gametips.platform.module.user.dto.LoginRequest;
import com.gametips.platform.module.user.dto.LoginResponse;
import com.gametips.platform.module.user.dto.RefreshRequest;
import com.gametips.platform.module.user.dto.RegisterRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

/**
 * 认证编排：注册 / 登录 / 刷新 / 登出。
 *
 * <h3>相对初版的安全加固</h3>
 * <ol>
 *   <li><b>登录失败锁定</b>：连续失败达阈值后临时锁定，抵御在线撞库（见 {@link LoginAttemptService}）；</li>
 *   <li><b>登录耗时恒定</b>：用户不存在时也执行一次 BCrypt 比对，
 *       避免通过响应时间差枚举用户名；</li>
 *   <li><b>统一错误文案</b>：无论是用户不存在还是密码错误，都返回「用户名或密码错误」；</li>
 *   <li><b>Refresh Token 轮换</b>：每次刷新作废旧令牌，并支持复用检测与主动吊销
 *       （见 {@link RefreshTokenService}）。</li>
 * </ol>
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserService userService;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    private final RefreshTokenService refreshTokenService;
    private final LoginAttemptService loginAttemptService;

    /**
     * 用于「用户不存在」分支的假比对。
     *
     * <p>如果不做这次比对，用户不存在时会直接抛异常返回（几毫秒），
     * 而用户存在时要等 BCrypt 算完（几十到上百毫秒），
     * 攻击者据此就能判断账号是否存在，这是典型的时序侧信道。
     *
     * <p>用构造期算好的固定哈希，避免每次请求再算一次 encode。
     */
    private volatile String dummyHashCache;

    /**
     * 懒加载假哈希。
     * 不能写成 final 字段初始化 —— Lombok 生成的构造器里 passwordEncoder
     * 是在构造器体内赋值的，字段初始化阶段它还是 null，会直接 NPE。
     */
    private String dummyHash() {
        String h = dummyHashCache;
        if (h == null) {
            synchronized (this) {
                h = dummyHashCache;
                if (h == null) {
                    h = passwordEncoder.encode(UUID.randomUUID().toString());
                    dummyHashCache = h;
                }
            }
        }
        return h;
    }

    @Transactional
    public LoginResponse register(RegisterRequest req, String clientIp, String userAgent) {
        User user = userService.register(req);
        List<String> roles = userService.getRoles(user.getId());
        return issueTokens(user, roles, clientIp, userAgent);
    }

    @Transactional
    public LoginResponse login(LoginRequest req, String clientIp, String userAgent) {
        // 已被锁定则直接拒绝，不再消耗 BCrypt 计算资源
        loginAttemptService.assertNotLocked(req.username(), clientIp);

        User user;
        try {
            user = userService.getByUsername(req.username());
        } catch (BizException notFound) {
            // 用户不存在：做一次等价耗时的假比对，然后按「密码错误」处理
            passwordEncoder.matches(req.password(), dummyHash());
            loginAttemptService.recordFailure(req.username(), clientIp);
            throw new BizException(ErrorCodes.UNAUTHORIZED, "用户名或密码错误");
        }

        if (!passwordEncoder.matches(req.password(), user.getPasswordHash())) {
            loginAttemptService.recordFailure(req.username(), clientIp);
            throw new BizException(ErrorCodes.UNAUTHORIZED, "用户名或密码错误");
        }

        if (user.getStatus() != UserStatus.NORMAL) {
            // 账号被禁用：不记为密码失败（避免管理员停用后仍触发锁定），但也不签发令牌
            throw new BizException(ErrorCodes.UNAUTHORIZED, "账号已被禁用");
        }

        loginAttemptService.clearFailures(req.username(), clientIp);
        List<String> roles = userService.getRoles(user.getId());
        return issueTokens(user, roles, clientIp, userAgent);
    }

    @Transactional
    public LoginResponse refresh(RefreshRequest req, String clientIp, String userAgent) {
        Long userId;
        try {
            userId = jwtService.extractUserId(req.refreshToken());
        } catch (Exception e) {
            throw new BizException(ErrorCodes.UNAUTHORIZED, "登录状态已失效，请重新登录");
        }

        // 先轮换（内部含复用检测），再加载用户：令牌无效时尽早失败
        String newRefresh = refreshTokenService.rotate(req.refreshToken(), clientIp, userAgent);

        User user = userService.getById(userId);
        if (user.getStatus() != UserStatus.NORMAL) {
            refreshTokenService.revokeAll(user.getId());
            throw new BizException(ErrorCodes.UNAUTHORIZED, "账号已被禁用");
        }

        List<String> roles = userService.getRoles(user.getId());
        String access = jwtService.generateAccessToken(user.getId(), user.getUsername(), roles);
        return LoginResponse.of(access, newRefresh, jwtService.accessTokenTtlSeconds(), user, roles);
    }

    /** 登出：吊销该用户全部 Refresh Token */
    @Transactional
    public void logout(Long userId) {
        refreshTokenService.revokeAll(userId);
    }

    private LoginResponse issueTokens(User user, List<String> roles,
                                      String clientIp, String userAgent) {
        String access = jwtService.generateAccessToken(user.getId(), user.getUsername(), roles);
        String refresh = refreshTokenService.issue(user.getId(), clientIp, userAgent);
        return LoginResponse.of(access, refresh, jwtService.accessTokenTtlSeconds(), user, roles);
    }
}
