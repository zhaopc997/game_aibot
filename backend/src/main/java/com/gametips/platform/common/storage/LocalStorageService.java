package com.gametips.platform.common.storage;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.LocalDate;
import java.util.UUID;

/**
 * 本地文件系统存储实现（MVP）。
 * 文件存放于 app.upload.local-dir 下，按日期分目录。
 */
@Slf4j
@Component
// 默认实现：未显式指定 app.storage.provider=cos 时使用本地磁盘，
// 保证本地开发无需任何云存储凭据即可跑通上传功能
@ConditionalOnProperty(name = "app.storage.provider", havingValue = "local", matchIfMissing = true)
public class LocalStorageService implements StorageService {

    private final Path root;

    public LocalStorageService(@Value("${app.upload.local-dir:./uploads}") String dir) {
        this.root = Path.of(dir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(root);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Override
    public String store(String key, InputStream in, String contentType, long size) {
        String safeKey = (key == null || key.isBlank())
                ? UUID.randomUUID().toString() : key;
        // 白名单字符，杜绝路径穿越与特殊字符文件名
        if (!safeKey.matches("[A-Za-z0-9._-]+")) {
            throw new IllegalArgumentException("非法文件名");
        }
        String dateDir = LocalDate.now().toString();
        Path dir = root.resolve(dateDir).normalize();
        Path target = dir.resolve(safeKey).normalize();
        // containment 双端校验：dir 与 target 都必须位于 root 之下
        if (!target.startsWith(root) || !dir.startsWith(root)) {
            throw new IllegalArgumentException("非法路径");
        }
        try {
            Files.createDirectories(dir);
            Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
            return "/uploads/" + dateDir + "/" + safeKey;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
