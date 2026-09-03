package com.gametips.platform.common.storage;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
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
        String dateDir = LocalDate.now().toString();
        Path dir = root.resolve(dateDir).normalize();
        if (!dir.startsWith(root)) {
            throw new IllegalArgumentException("非法路径");
        }
        try {
            Files.createDirectories(dir);
            Path target = dir.resolve(safeKey).normalize();
            Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
            return "/uploads/" + dateDir + "/" + safeKey;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
