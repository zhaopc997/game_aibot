package com.gametips.platform;

import org.junit.jupiter.api.Test;
import org.springframework.http.server.PathContainer;
import org.springframework.web.util.pattern.PathPattern;
import org.springframework.web.util.pattern.PathPatternParser;

import static org.assertj.core.api.Assertions.assertThat;

class SecurityConfigMatcherTest {

    @Test
    void testPathPatternMatching() {
        PathPatternParser parser = new PathPatternParser();
        PathPattern pattern = parser.parse("/api/v1/games/**");

        PathContainer pathWithoutSlash = PathContainer.parsePath("/api/v1/games");
        PathContainer pathWithSlash = PathContainer.parsePath("/api/v1/games/");
        PathContainer pathWithId = PathContainer.parsePath("/api/v1/games/1");

        System.out.println("matches without slash (/api/v1/games): " + pattern.matches(pathWithoutSlash));
        System.out.println("matches with slash (/api/v1/games/): " + pattern.matches(pathWithSlash));
        System.out.println("matches with id (/api/v1/games/1): " + pattern.matches(pathWithId));

        assertThat(pattern.matches(pathWithoutSlash)).isTrue();
    }
}
