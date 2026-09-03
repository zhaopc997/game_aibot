package com.gametips.platform.module.ai.service;

import com.gametips.platform.module.ai.domain.AiParseTask;
import com.gametips.platform.module.ai.domain.AiTaskStatus;
import com.gametips.platform.module.ai.repository.AiParseTaskRepository;
import com.gametips.platform.module.ai.service.llm.LlmClient;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.notification.service.NotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * AI 解析异步处理管线：
 * 提取原始内容 → 调用大模型 → JSON 校验 → 降级 → 生成攻略草稿 → 通知用户。
 * MVP 阶段使用 @Async 线程池；第二阶段接入 RabbitMQ 解耦与重试。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AiParseProcessor {

    private final AiParseTaskRepository taskRepository;
    private final GuideRepository guideRepository;
    private final LlmClient llmClient;
    private final AiContentValidator validator;
    private final NotificationService notificationService;

    @Async("aiTaskExecutor")
    public void process(Long taskId) {
        AiParseTask task = taskRepository.findById(taskId).orElse(null);
        if (task == null) {
            return;
        }
        task.setStatus(AiTaskStatus.PROCESSING);
        taskRepository.save(task);
        try {
            // 1. 提取原始内容（MVP 从 source_url 简单取默认文本；真实接入抽帧/ASR/HTML 解析）
            String raw = extractRaw(task.getSourceType(), task.getSourceUrl());
            // 2. 调用大模型
            Map<String, Object> llmOutput = llmClient.parseGuide(task.getSourceType(), raw);
            // 3. 校验 + 降级
            Map<String, Object> content = validator.validateAndNormalize(llmOutput);

            Guide guide = new Guide();
            guide.setType("AI_GENERATED");
            guide.setGameId(1L); // MVP 默认游戏占位，后续映射解析来源所关联的游戏
            guide.setTitle("AI 生成：" + (task.getSourceUrl() == null ? "来源" : task.getSourceUrl()));
            guide.setContent(content);
            guide.setStatus(GuideStatus.DRAFT);
            guide.setAuthorId(1L); // 系统/超管占位，后续映射提交者
            guide = guideRepository.save(guide);

            task.setResultGuideId(guide.getId());
            task.setStatus(AiTaskStatus.SUCCEEDED);
            taskRepository.save(task);

            notificationService.create(guide.getAuthorId(), "AI_TASK_DONE",
                    "AI 解析完成", "攻略草稿已生成，请查看并编辑后提交审核。",
                    "guide", guide.getId());
        } catch (Exception e) {
            log.error("ai parse failed, taskId={}", taskId, e);
            task.setStatus(AiTaskStatus.FAILED);
            task.setErrorMsg(e.getMessage());
            taskRepository.save(task);
        }
    }

    private String extractRaw(String sourceType, String sourceUrl) {
        if (sourceUrl == null) {
            return "示例文本：进入副本 - 击败首领 - 拾取奖励";
        }
        return "示例解析内容（" + sourceType + "）：" + sourceUrl;
    }
}
