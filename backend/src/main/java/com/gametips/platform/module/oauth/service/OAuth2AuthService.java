package com.gametips.platform.module.oauth.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.oauth.config.OAuthProperties;
import com.gametips.platform.module.oauth.domain.OAuthAccount;
import com.gametips.platform.module.oauth.repository.OAuthAccountRepository;
import com.gametips.platform.module.user.domain.Role;
import com.gametips.platform.module.user.domain.User;
import com.gametips.platform.module.user.domain.UserRole;
import com.gametips.platform.module.user.domain.UserStatus;
import com.gametips.platform.module.user.dto.LoginResponse;
import com.gametips.platform.module.user.repository.UserRepository;
import com.gametips.platform.module.user.repository.UserRoleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * OAuth 第三方登录：按 (provider, externalId) 查找或创建本地用户并关联 OAuth 账号。
 * 支持：
 *   - 模拟模式（app.oauth.mock=true）：POST /auth/oauth/mock 免凭据登录，便于本地调试。
 *   - 真实模式：Spring Security OAuth2 登录成功后由 OAuth2LoginSuccessHandler 调用。
 */
@Service
@RequiredArgsConstructor
public class OAuth2AuthService {

    private final OAuthProperties properties;
    private final OAuthAccountRepository oauthAccountRepository;
    private final UserRepository userRepository;
    private final UserRoleRepository userRoleRepository;
    private final PasswordEncoder passwordEncoder;
    private final com.gametips.platform.common.security.JwtService jwtService;

    public List<String> enabledProviders() {
        return properties.getProviders().entrySet().stream()
                .filter(e -> e.getValue().isEnabled())
                .map(Map.Entry::getKey)
                .toList();
    }

    /**
     * 模拟登录（mock 模式）：根据 provider + code 生成稳定的外部标识。
     * code 形如 "mock-<provider>-<任意字符串>"，真实接入时由 OAuth 回调携带。
     */
    @Transactional
    public LoginResponse mockLogin(String provider, String code) {
        if (!properties.isMock()) {
            throw new BizException(ErrorCodes.FORBIDDEN, "模拟登录未开启");
        }
        String externalId = "mock-" + provider + "-" + (code == null ? UUID.randomUUID() : code);
        String username = provider + "_" + externalId.substring(externalId.length() - 6);
        return loginWithProfile(provider, externalId, username, null);
    }

    /**
     * 真实 OAuth 登录成功后的统一入口。
     */
    @Transactional
    public LoginResponse loginWithProfile(String provider, String externalId,
                                          String externalUsername, String avatarUrl) {
        OAuthAccount account = oauthAccountRepository.findByProviderAndExternalId(provider, externalId)
                .orElseGet(() -> createUserAndLink(provider, externalId, externalUsername, avatarUrl));

        User user = userRepository.findById(account.getUserId())
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "关联用户不存在"));
        List<String> roles = userRoleRepository.findByUserId(user.getId()).stream()
                .map(UserRole::getRole).map(Enum::name).toList();

        String access = jwtService.generateAccessToken(user.getId(), user.getUsername(), roles);
        String refresh = jwtService.generateRefreshToken(user.getId());
        return LoginResponse.of(access, refresh, jwtService.accessTokenTtlSeconds(), user, roles);
    }

    private OAuthAccount createUserAndLink(String provider, String externalId,
                                           String externalUsername, String avatarUrl) {
        User user = new User();
        user.setUsername(externalUsername == null || externalUsername.isBlank()
                ? provider + "_" + externalId.hashCode() : externalUsername);
        user.setEmail(user.getUsername() + "@oauth.local");
        user.setPasswordHash(passwordEncoder.encode(UUID.randomUUID().toString()));
        user.setStatus(UserStatus.NORMAL);
        user = userRepository.save(user);
        userRoleRepository.save(new UserRole(user.getId(), Role.USER));

        OAuthAccount account = new OAuthAccount();
        account.setUserId(user.getId());
        account.setProvider(provider);
        account.setExternalId(externalId);
        account.setExternalUsername(externalUsername);
        account.setAvatarUrl(avatarUrl);
        return oauthAccountRepository.save(account);
    }
}
