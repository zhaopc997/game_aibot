package com.gametips.platform.module.user.dto;

import com.gametips.platform.module.user.domain.User;

import java.util.List;

public record UserResponse(
        Long id,
        String username,
        String email,
        String avatar,
        String bio,
        Integer level,
        Long exp,
        List<String> roles
) {
    public static UserResponse from(User u, List<String> roles) {
        return new UserResponse(
                u.getId(), u.getUsername(), u.getEmail(),
                u.getAvatar(), u.getBio(), u.getLevel(), u.getExp(),
                roles == null ? List.of() : roles);
    }

    public static UserResponse from(User u) {
        return from(u, List.of());
    }
}
