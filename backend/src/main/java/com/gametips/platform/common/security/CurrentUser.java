package com.gametips.platform.common.security;

import lombok.Getter;

import java.util.List;

/**
 * 从 SecurityContext 获取当前登录用户。
 */
public final class CurrentUser {

    private CurrentUser() {}

    @Getter
    public static class Context {
        private final Long userId;
        private final String username;
        private final List<String> roles;

        public Context(LoginUser loginUser) {
            this.userId = loginUser.userId();
            this.username = loginUser.username();
            this.roles = loginUser.roles();
        }
    }

    public static Context get() {
        var auth = org.springframework.security.core.context.SecurityContextHolder
                .getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof LoginUser loginUser) {
            return new Context(loginUser);
        }
        throw new org.springframework.security.access.AccessDeniedException("未登录");
    }

    public static Long userId() {
        return get().getUserId();
    }

    public static boolean hasRole(String role) {
        return get().getRoles().contains(role);
    }
}
