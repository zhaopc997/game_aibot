package com.gametips.platform.module.oauth.web;

import com.gametips.platform.module.oauth.config.OAuthProperties;
import com.gametips.platform.module.oauth.service.OAuth2AuthService;
import com.gametips.platform.module.user.dto.LoginResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.web.authentication.SavedRequestAwareAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * OAuth2 登录成功：提取供应商用户信息 → find-or-create 本地用户 → 签发 JWT → 重定向前端。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class OAuth2LoginSuccessHandler extends SavedRequestAwareAuthenticationSuccessHandler {

    private final OAuth2AuthService oauth2AuthService;
    private final OAuthProperties properties;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                        Authentication authentication) throws IOException {
        OAuth2AuthenticationToken token = (OAuth2AuthenticationToken) authentication;
        String provider = token.getAuthorizedClientRegistrationId();
        var attrs = token.getPrincipal().getAttributes();

        String externalId = String.valueOf(attrs.get("id") != null
                ? attrs.get("id") : attrs.get("sub"));
        String username = (String) attrs.getOrDefault("login",
                (String) attrs.getOrDefault("name", provider + "_user"));
        String avatar = (String) attrs.getOrDefault("avatar_url",
                (String) attrs.getOrDefault("picture", null));

        LoginResponse login = oauth2AuthService.loginWithProfile(provider, externalId, username, avatar);
        String url = properties.getRedirectUrl() + "?accessToken=" + login.accessToken()
                + "&refreshToken=" + login.refreshToken();
        log.info("oauth login success, provider={}, externalId={}", provider, externalId);
        getRedirectStrategy().sendRedirect(request, response, url);
    }
}
