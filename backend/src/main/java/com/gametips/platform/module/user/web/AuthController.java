package com.gametips.platform.module.user.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.user.dto.LoginRequest;
import com.gametips.platform.module.user.dto.LoginResponse;
import com.gametips.platform.module.user.dto.RefreshRequest;
import com.gametips.platform.module.user.dto.RegisterRequest;
import com.gametips.platform.module.user.dto.UserResponse;
import com.gametips.platform.module.user.service.AuthService;
import com.gametips.platform.module.user.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final UserService userService;

    @PostMapping("/auth/register")
    public ApiResponse<LoginResponse> register(@Valid @RequestBody RegisterRequest req) {
        return ApiResponse.ok(authService.register(req));
    }

    @PostMapping("/auth/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest req) {
        return ApiResponse.ok(authService.login(req));
    }

    @PostMapping("/auth/refresh")
    public ApiResponse<LoginResponse> refresh(@Valid @RequestBody RefreshRequest req) {
        return ApiResponse.ok(authService.refresh(req));
    }

    @GetMapping("/users/me")
    public ApiResponse<UserResponse> me() {
        Long userId = CurrentUser.userId();
        var user = userService.getById(userId);
        return ApiResponse.ok(UserResponse.from(user, userService.getRoles(userId)));
    }
}
