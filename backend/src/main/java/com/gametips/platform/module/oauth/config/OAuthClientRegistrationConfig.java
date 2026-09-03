package com.gametips.platform.module.oauth.config;

import com.gametips.platform.module.oauth.web.OAuth2LoginSuccessHandler;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.security.oauth2.core.ClientAuthenticationMethod;

import java.util.HashMap;
import java.util.Map;

/**
 * 从 OAuthProperties 构建 OAuth2 ClientRegistration。
 * GitHub/WeChat 使用标准授权码模式；Steam 走 OpenID（可后续补充自定义）。
 */
@Configuration
@RequiredArgsConstructor
public class OAuthClientRegistrationConfig {

    private final OAuthProperties properties;

    @Bean
    public ClientRegistrationRepository clientRegistrationRepository() {
        Map<String, ClientRegistration> registrations = new HashMap<>();
        for (Map.Entry<String, OAuthProperties.Provider> e : properties.getProviders().entrySet()) {
            OAuthProperties.Provider p = e.getValue();
            if (!p.isEnabled()) {
                continue;
            }
            registrations.put(e.getKey(), ClientRegistration.withRegistrationId(e.getKey())
                    .clientId(p.getClientId())
                    .clientSecret(p.getClientSecret())
                    .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
                    .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
                    .redirectUri("{baseUrl}/login/oauth2/code/{registrationId}")
                    .authorizationUri(p.getAuthorizationUri())
                    .tokenUri(p.getTokenUri())
                    .userInfoUri(p.getUserInfoUri())
                    .userNameAttributeName(p.getUserNameAttribute())
                    .scope(p.getScope().split("\\s+"))
                    .build());
        }
        // Map 构造器允许空注册表（mock 模式无需注册真实 provider）
        return new InMemoryClientRegistrationRepository(registrations);
    }
}
