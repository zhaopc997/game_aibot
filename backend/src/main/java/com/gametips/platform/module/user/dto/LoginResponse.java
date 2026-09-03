package com.gametips.platform.module.user.dto;

import com.gametips.platform.module.user.domain.User;

import java.util.List;

public record LoginResponse(
        String accessToken,
        String refreshToken,
        long expiresIn,
        UserResponse user
) {
    public static LoginResponse of(String accessToken, String refreshToken, long expiresIn,
                                   User user, List<String> roles) {
        return new LoginResponse(accessToken, refreshToken, expiresIn,
                UserResponse.from(user, roles));
    }
}
