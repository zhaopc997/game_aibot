package com.gametips.platform.module.user.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.ClientIpResolver;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.user.dto.LoginRequest;
import com.gametips.platform.module.user.dto.LoginResponse;
import com.gametips.platform.module.user.dto.RefreshRequest;
import com.gametips.platform.module.user.dto.RegisterRequest;
import com.gametips.platform.module.user.dto.UserResponse;
import com.gametips.platform.module.user.service.AuthService;
import com.gametips.platform.module.user.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final UserService userService;

    @PostMapping("/auth/register")
    public ApiResponse<LoginResponse> register(@Valid @RequestBody RegisterRequest req,
                                               HttpServletRequest http) {
        return ApiResponse.ok(authService.register(req, clientIp(http), userAgent(http)));
    }

    @PostMapping("/auth/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest req,
                                            HttpServletRequest http) {
        return ApiResponse.ok(authService.login(req, clientIp(http), userAgent(http)));
    }

    @PostMapping("/auth/refresh")
    public ApiResponse<LoginResponse> refresh(@Valid @RequestBody RefreshRequest req,
                                              HttpServletRequest http) {
        return ApiResponse.ok(authService.refresh(req, clientIp(http), userAgent(http)));
    }

    /**
     * 登出：吊销当前用户全部 Refresh Token。
     *
     * <p>JWT 是无状态的，Access Token 无法立刻作废（30 分钟内仍有效，
     * 这是有意的权衡：否则每个请求都要查库）。但 Refresh Token 一旦吊销，
     * 攻击者最迟 30 分钟后就无法再续期，泄露窗口从「7 天」缩短到「30 分钟」。
     */
    @PostMapping("/auth/logout")
    public ApiResponse<Map<String, Object>> logout() {
        authService.logout(CurrentUser.userId());
        return ApiResponse.ok(Map.of("loggedOut", true));
    }

    @GetMapping("/users/me")
    public ApiResponse<UserResponse> me() {
        Long userId = CurrentUser.userId();
        var user = userService.getById(userId);
        return ApiResponse.ok(UserResponse.from(user, userService.getRoles(userId)));
    }

    /** 取真实客户端 IP（见 ClientIpResolver 的链路说明） */
    private static String clientIp(HttpServletRequest req) {
        return ClientIpResolver.resolve(req);
    }

    private static String userAgent(HttpServletRequest req) {
        String ua = req.getHeader("User-Agent");
        return ua == null ? "" : ua;
    }
}
