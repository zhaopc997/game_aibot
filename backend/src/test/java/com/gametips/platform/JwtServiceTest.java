package com.gametips.platform;

import com.gametips.platform.common.security.JwtService;
import io.jsonwebtoken.Claims;
import org.junit.jupiter.api.Test;

import java.time.Duration;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class JwtServiceTest {

    private final JwtService jwtService = new JwtService(
            "test-secret-key-for-junit-0123456789abcdef0123456789abcdef",
            Duration.ofMinutes(30),
            Duration.ofDays(7));

    @Test
    void generateAndParseAccessToken() {
        String token = jwtService.generateAccessToken(42L, "alice", List.of("USER", "CREATOR"));
        Claims claims = jwtService.parse(token);
        assertThat(claims.getSubject()).isEqualTo("42");
        assertThat(claims.get("username", String.class)).isEqualTo("alice");
        assertThat(claims.get("roles", List.class)).containsExactly("USER", "CREATOR");
    }

    @Test
    void extractUserIdFromRefreshToken() {
        String token = jwtService.generateRefreshToken(7L);
        assertThat(jwtService.extractUserId(token)).isEqualTo(7L);
    }
}
