package com.gametips.platform.module.upload.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.common.storage.StorageService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;
import java.util.Set;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/uploads")
@RequiredArgsConstructor
public class UploadController {

    private static final long MAX_SIZE = 20L * 1024 * 1024; // 20MB
    private static final Set<String> ALLOWED_EXT = Set.of(
            ".jpg", ".jpeg", ".png", ".gif", ".webp",
            ".mp4", ".webm", ".mov");

    private final StorageService storageService;

    @PostMapping
    public ApiResponse<Map<String, String>> upload(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            throw new BizException(ErrorCodes.PARAM_ERROR, "文件不能为空");
        }
        if (file.getSize() > MAX_SIZE) {
            throw new BizException(ErrorCodes.PARAM_ERROR, "文件大小超过限制(20MB)");
        }
        String contentType = file.getContentType();
        if (contentType == null || (!contentType.startsWith("image/") && !contentType.startsWith("video/"))) {
            throw new BizException(ErrorCodes.PARAM_ERROR, "不支持的文件MIME类型");
        }
        if (contentType.toLowerCase().contains("svg") || contentType.toLowerCase().contains("html")) {
            throw new BizException(ErrorCodes.PARAM_ERROR, "不支持的文件类型(禁止包含脚本载荷)");
        }
        String original = file.getOriginalFilename();
        String ext = "";
        if (original != null && original.contains(".")) {
            ext = original.substring(original.lastIndexOf('.')).toLowerCase();
        }
        if (!ALLOWED_EXT.contains(ext)) {
            throw new BizException(ErrorCodes.PARAM_ERROR, "不支持的文件扩展名");
        }
        String key = UUID.randomUUID() + ext;
        String url;
        try (var in = file.getInputStream()) {
            url = storageService.store(key, in, file.getContentType(), file.getSize());
        } catch (Exception e) {
            throw new IllegalStateException("上传失败", e);
        }
        return ApiResponse.ok(Map.of("url", url));
    }
}
