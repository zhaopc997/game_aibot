package com.gametips.platform.module.ai.service;

import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.ai.domain.AiQaLog;
import com.gametips.platform.module.ai.repository.AiQaLogRepository;
import com.gametips.platform.module.ai.service.llm.LlmClient;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class AiQaService {

    private final LlmClient llmClient;
    private final AiQaLogRepository qaLogRepository;
    private final GuideRepository guideRepository;

    @Transactional
    public AiQaLog ask(String question) {
        // MVP：从已发布攻略摘要拼接上下文；正式版检索相关攻略
        String context = guideRepository.findTop3ByStatusOrderByUpdatedAtDesc(GuideStatus.PUBLISHED)
                .stream().limit(3).map(Guide::getTitle).reduce((a, b) -> a + "；" + b).orElse("暂无攻略");
        String answer = llmClient.chat(question, context);

        AiQaLog log = new AiQaLog();
        log.setUserId(CurrentUser.userId());
        log.setQuestion(question);
        log.setAnswer(answer);
        return qaLogRepository.save(log);
    }

    @Transactional
    public Guide generateDraft(String notes) {
        Map<String, Object> raw = llmClient.generateDraft(notes);
        Guide guide = new Guide();
        guide.setType("AI_GENERATED");
        guide.setGameId(1L); // MVP 默认游戏占位
        guide.setTitle("AI 草稿：" + (notes.length() > 20 ? notes.substring(0, 20) : notes));
        guide.setContent(raw);
        guide.setStatus(GuideStatus.DRAFT);
        guide.setAuthorId(CurrentUser.userId());
        return guideRepository.save(guide);
    }
}
