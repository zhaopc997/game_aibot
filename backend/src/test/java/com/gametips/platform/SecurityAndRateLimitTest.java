package com.gametips.platform;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.ratelimit.RateLimitInterceptor;
import com.gametips.platform.common.ratelimit.RateLimiter;
import com.gametips.platform.common.storage.StorageService;
import com.gametips.platform.module.upload.web.UploadController;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockMultipartFile;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class SecurityAndRateLimitTest {

    @Test
    void uploadShouldRejectSvgFile() {
        StorageService storageService = mock(StorageService.class);
        UploadController controller = new UploadController(storageService);

        MockMultipartFile svgFile = new MockMultipartFile(
                "file", "payload.svg", "image/svg+xml",
                "<svg onload='alert(1)'></svg>".getBytes()
        );

        assertThatThrownBy(() -> controller.upload(svgFile))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("不支持的文件类型");
    }

    @Test
    void uploadShouldRejectNonMediaMimeType() {
        StorageService storageService = mock(StorageService.class);
        UploadController controller = new UploadController(storageService);

        MockMultipartFile exeFile = new MockMultipartFile(
                "file", "exploit.png", "application/x-msdownload",
                "malicious bytes".getBytes()
        );

        assertThatThrownBy(() -> controller.upload(exeFile))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("不支持的文件MIME类型");
    }

    @Test
    void uploadShouldAcceptStandardImage() {
        StorageService storageService = mock(StorageService.class);
        when(storageService.store(any(), any(), any(), org.mockito.ArgumentMatchers.anyLong()))
                .thenReturn("/uploads/2026-10-22/test.png");

        UploadController controller = new UploadController(storageService);
        MockMultipartFile validPng = new MockMultipartFile(
                "file", "valid.png", "image/png",
                new byte[]{1, 2, 3, 4}
        );

        var resp = controller.upload(validPng);
        assertThat(resp.getCode()).isEqualTo(0);
        assertThat(resp.getData()).containsKey("url");
    }

    @Test
    void rateLimitInterceptorShouldClassifyAgentChatAsAiResource() throws Exception {
        RateLimiter rateLimiter = mock(RateLimiter.class);
        when(rateLimiter.allow(eq("ai"), any(), any(Duration.class), eq(10))).thenReturn(true);

        RateLimitInterceptor interceptor = new RateLimitInterceptor(rateLimiter);

        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/agent/chat");
        request.addHeader("X-Real-IP", "203.0.113.195");
        MockHttpServletResponse response = new MockHttpServletResponse();

        boolean allowed = interceptor.preHandle(request, response, new Object());
        assertThat(allowed).isTrue();

        verify(rateLimiter).allow(eq("ai"), eq("ip:203.0.113.195"), any(Duration.class), eq(10));
    }
}
