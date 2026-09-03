package com.gametips.platform.common.storage;

import java.io.InputStream;

/**
 * 对象存储抽象。
 * MVP 使用本地文件系统实现；生产可替换为 MinIO / 阿里云 OSS / AWS S3。
 */
public interface StorageService {

    /**
     * 保存文件，返回可访问 URL。
     */
    String store(String key, InputStream in, String contentType, long size);

    /**
     * 生成预签名上传 URL（MVP 本地实现返回空，直接走 store）。
     */
    default String presignedUploadUrl(String key) {
        return null;
    }

    /**
     * 生成预签名下载/访问 URL（MVP 直接返回固定 URL）。
     */
    default String presignedAccessUrl(String key) {
        return null;
    }
}
