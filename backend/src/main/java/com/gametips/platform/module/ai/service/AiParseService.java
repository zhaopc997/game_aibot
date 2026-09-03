package com.gametips.platform.module.ai.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.ai.domain.AiParseTask;
import com.gametips.platform.module.ai.domain.AiTaskStatus;
import com.gametips.platform.module.ai.repository.AiParseTaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;

/**
 * AI 聚合解析任务：以 source_hash 保证幂等（数据库唯一约束兜底）。
 * 提交后异步处理（AiParseProcessor）。
 *
 * 注意：submit 不置于事务内，避免与 @Async 处理器形成同步事务嵌套，
 * 由 processor 内部逐步自管理事务。
 */
@Service
@RequiredArgsConstructor
public class AiParseService {

    private final AiParseTaskRepository taskRepository;
    private final AiParseProcessor processor;

    public AiParseTask submit(String sourceType, String sourceUrl) {
        String hash = sha256(sourceUrl == null ? sourceType + System.nanoTime() : sourceUrl);
        AiParseTask task = taskRepository.findBySourceHash(hash)
                .orElseGet(() -> {
                    AiParseTask t = new AiParseTask();
                    t.setSourceType(sourceType);
                    t.setSourceUrl(sourceUrl);
                    t.setSourceHash(hash);
                    t.setStatus(AiTaskStatus.PENDING);
                    return taskRepository.save(t);
                });
        // 已成功过的任务直接复用，不重复处理
        if (task.getStatus() == AiTaskStatus.PENDING || task.getStatus() == AiTaskStatus.FAILED) {
            processor.process(task.getId());
        }
        return task;
    }

    public AiParseTask getStatus(Long taskId) {
        return taskRepository.findById(taskId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "任务不存在"));
    }

    private String sha256(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(md.digest(input.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }
}
