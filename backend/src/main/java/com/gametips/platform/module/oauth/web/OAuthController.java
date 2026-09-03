package com.gametips.platform.module.oauth.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.module.oauth.config.OAuthProperties;
import com.gametips.platform.module.oauth.service.OAuth2AuthService;
import com.gametips.platform.module.user.dto.LoginResponse;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/auth/oauth")
@RequiredArgsConstructor
public class OAuthController {

    private final OAuth2AuthService oauth2AuthService;
    private final OAuthProperties properties;

    /**
     * 已启用的供应商列表（前端渲染登录按钮）。
     */
    @GetMapping("/providers")
    public ApiResponse<Map<String, Object>> providers() {
        return ApiResponse.ok(Map.of(
                "mock", properties.isMock(),
                "providers", oauth2AuthService.enabledProviders(),
                "authorizeUrl", "/oauth2/authorization/"));
    }

    /**
     * 模拟登录（仅 mock 模式开启时可用）。
     * code 任意字符串，示例：POST /api/v1/auth/oauth/mock?provider=github&code=demo
     */
    @PostMapping("/mock")
    public ApiResponse<LoginResponse> mock(@RequestParam @NotBlank String provider,
                                           @RequestParam(required = false) String code) {
        return ApiResponse.ok(oauth2AuthService.mockLogin(provider, code));
    }
}
