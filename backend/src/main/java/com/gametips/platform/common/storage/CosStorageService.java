package com.gametips.platform.common.storage;

import com.qcloud.cos.COSClient;
import com.qcloud.cos.ClientConfig;
import com.qcloud.cos.auth.BasicCOSCredentials;
import com.qcloud.cos.auth.COSCredentials;
import com.qcloud.cos.model.CannedAccessControlList;
import com.qcloud.cos.model.ObjectMetadata;
import com.qcloud.cos.model.PutObjectRequest;
import com.qcloud.cos.region.Region;
import jakarta.annotation.PreDestroy;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.io.InputStream;
import java.time.LocalDate;
import java.util.UUID;

/**
 * 腾讯云 COS 对象存储实现。
 *
 * <p>启用方式：{@code app.storage.provider=cos}（默认是 local）。
 * 未配置时会话退回 {@link LocalStorageService}，本地开发无需任何云凭据。
 *
 * <h3>为什么上传文件要放对象存储</h3>
 * 本地磁盘实现有两个问题：
 * <ol>
 *   <li>用户上传的图片/视频会持续占用服务器磁盘，且无法随容器水平扩容；</li>
 *   <li>文件只能由本机 Nginx 提供，无法享受 CDN 加速。</li>
 * </ol>
 *
 * <h3>对象命名</h3>
 * {@code uploads/yyyy-MM-dd/<uuid>.<ext>}。用 UUID 而非原始文件名，
 * 避免用户文件名带来的特殊字符、路径穿越与同名覆盖问题。
 */
@Slf4j
@Component
@ConditionalOnProperty(name = "app.storage.provider", havingValue = "cos")
public class CosStorageService implements StorageService {

    private final COSClient client;
    private final String bucket;
    private final String region;
    private final String publicDomain;
    private final String prefix;

    public CosStorageService(
            @Value("${app.storage.cos.secret-id}") String secretId,
            @Value("${app.storage.cos.secret-key}") String secretKey,
            @Value("${app.storage.cos.bucket}") String bucket,
            @Value("${app.storage.cos.region}") String region,
            @Value("${app.storage.cos.public-domain:}") String publicDomain,
            @Value("${app.storage.cos.prefix:uploads}") String prefix) {
        this.bucket = bucket;
        this.region = region;
        this.publicDomain = publicDomain == null ? "" : publicDomain.replaceAll("/+$", "");
        this.prefix = prefix;

        COSCredentials cred = new BasicCOSCredentials(secretId, secretKey);
        ClientConfig cfg = new ClientConfig(new Region(region));
        // 上传大文件（视频）时的超时与重试
        cfg.setConnectionTimeout(30_000);
        cfg.setSocketTimeout(300_000);
        this.client = new COSClient(cred, cfg);
        log.info("[storage] 使用 COS 存储：bucket={} region={} domain={}",
                bucket, region, this.publicDomain.isEmpty() ? "(默认域名)" : this.publicDomain);
    }

    @Override
    public String store(String key, InputStream in, String contentType, long size) {
        String ext = extensionOf(key);
        String objectKey = "%s/%s/%s%s".formatted(prefix, LocalDate.now(), UUID.randomUUID(), ext);

        ObjectMetadata meta = new ObjectMetadata();
        if (contentType != null && !contentType.isBlank()) {
            meta.setContentType(contentType);
        }
        // 上传内容不可变（UUID 命名），可长期缓存
        meta.setCacheControl("public, max-age=31536000, immutable");
        if (size > 0) {
            meta.setContentLength(size);
        }

        PutObjectRequest req = new PutObjectRequest(bucket, objectKey, in, meta);
        // 桶若为私有读，这里保证上传后的文件可被浏览器直接访问
        req.setCannedAcl(CannedAccessControlList.PublicRead);
        client.putObject(req);

        String url = publicDomain.isEmpty()
                ? "https://%s.cos.%s.myqcloud.com/%s".formatted(bucket, region, objectKey)
                : publicDomain + "/" + objectKey;
        log.debug("[storage] 已上传 {} → {}", objectKey, url);
        return url;
    }

    /** 取出原始扩展名（含点），仅允许安全字符，最长 10 位。 */
    private static String extensionOf(String key) {
        if (key == null) {
            return "";
        }
        int dot = key.lastIndexOf('.');
        if (dot < 0 || dot == key.length() - 1) {
            return "";
        }
        String ext = key.substring(dot).toLowerCase();
        return ext.matches("\\.[a-z0-9]{1,10}") ? ext : "";
    }

    @PreDestroy
    public void shutdown() {
        client.shutdown();
        log.info("[storage] COS 客户端已关闭");
    }
}
