package com.gametips.platform.module.oauth.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * OAuth2 供应商配置（配置驱动）。
 * app.oauth.mock=true 时启用模拟登录（无需真实凭据，便于本地调试）。
 * providers 下可配置 github / steam / wechat 等。
 */
@Data
@Component
@ConfigurationProperties(prefix = "app.oauth")
public class OAuthProperties {

    /** 无真实凭据时的模拟登录开关 */
    private boolean mock = true;

    /** 前端登录成功后的跳转地址 */
    private String redirectUrl = "http://localhost:5173/oauth/callback";

    /** 供应商注册表 */
    private Map<String, Provider> providers = new HashMap<>();

    @Data
    public static class Provider {
        private boolean enabled = false;
        private String clientId = "";
        private String clientSecret = "";
        private String authorizationUri;
        private String tokenUri;
        private String userInfoUri;
        private String userNameAttribute = "id";
        private String scope = "";
    }
}
