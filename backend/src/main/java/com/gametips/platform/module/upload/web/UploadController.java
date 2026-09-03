package com.gametips.platform.module.upload.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.storage.StorageService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/uploads")
@RequiredArgsConstructor
public class UploadController {

    private final StorageService storageService;

    @PostMapping
    public ApiResponse<Map<String, String>> upload(@RequestParam("file") MultipartFile file) {
        String original = file.getOriginalFilename();
        String ext = "";
        if (original != null && original.contains(".")) {
            ext = original.substring(original.lastIndexOf('.'));
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
