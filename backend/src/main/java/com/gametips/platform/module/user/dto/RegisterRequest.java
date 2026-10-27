package com.gametips.platform.module.user.dto;

import com.gametips.platform.common.validation.StrongPassword;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record RegisterRequest(
        @NotBlank @Size(min = 3, max = 64) String username,
        @NotBlank @Email String email,
        // 原为 @Size(min=6)，实测 12345678 可通过；改为强度校验
        @NotBlank @StrongPassword String password
) {}
