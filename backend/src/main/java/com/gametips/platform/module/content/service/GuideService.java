package com.gametips.platform.module.content.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.version.domain.GuideVersionHistory;
import com.gametips.platform.module.version.repository.GuideVersionHistoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class GuideService {

    private final GuideRepository guideRepository;
    private final GuideVersionHistoryRepository historyRepository;
    private final com.gametips.platform.module.review.service.ContentReviewService contentReviewService;
    private final org.springframework.beans.factory.ObjectProvider<com.gametips.platform.module.search.service.GuideIndexService> guideIndexProvider;

    @Transactional
    public Guide create(Guide guide) {
        guide.setId(null);
        guide.setStatus(GuideStatus.DRAFT);
        return guideRepository.save(guide);
    }

    @org.springframework.cache.annotation.Cacheable(cacheNames = "guide:detail", key = "#id")
    public Guide get(Long id) {
        return guideRepository.findById(id)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "攻略不存在"));
    }

    @org.springframework.cache.annotation.CacheEvict(cacheNames = "guide:detail", key = "#id")
    @Transactional
    public Guide update(Long id, Guide update) {
        Guide guide = get(id);
        guide.setTitle(update.getTitle());
        guide.setSummary(update.getSummary());
        guide.setContent(update.getContent());
        guide.setTags(update.getTags());
        guide.setDifficulty(update.getDifficulty());
        guide.setVersionId(update.getVersionId());
        return guideRepository.save(guide);
    }

    @org.springframework.cache.annotation.CacheEvict(cacheNames = "guide:detail", key = "#id")
    @Transactional
    public void submitReview(Long id, Long operatorId) {
        Guide guide = get(id);
        ensureOwnerOrAdmin(guide, operatorId);
        if (guide.getStatus() != GuideStatus.DRAFT) {
            throw new BizException(ErrorCodes.CONFLICT, "仅草稿可提交审核");
        }
        guide.setStatus(GuideStatus.PENDING_REVIEW);
        guideRepository.save(guide);
        // 触发内容审核：机器判定风险，LOW/MEDIUM 自动发布，HIGH 进入人工队列
        String text = guide.getTitle() + " " + guide.getSummary()
                + " " + String.join(",", guide.getTags() == null ? List.of() : guide.getTags());
        contentReviewService.submit("guide", guide.getId(), text);
    }

    @org.springframework.cache.annotation.CacheEvict(cacheNames = "guide:detail", key = "#id")
    @Transactional
    public void markOutdated(Long id, Long operatorId) {
        Guide guide = get(id);
        ensureOwnerOrAdmin(guide, operatorId);
        guide.setStatus(GuideStatus.OUTDATED);
        guideRepository.save(guide);
    }

    @org.springframework.cache.annotation.CacheEvict(cacheNames = "guide:detail", key = "#id")
    @Transactional
    public void claimCompatible(Long id, Long authorId) {
        Guide guide = get(id);
        ensureOwnerOrAdmin(guide, authorId);
        if (guide.getStatus() != GuideStatus.PENDING_VERIFICATION
                && guide.getStatus() != GuideStatus.OUTDATED) {
            throw new BizException(ErrorCodes.CONFLICT, "当前状态无需声明兼容");
        }
        guide.setStatus(GuideStatus.PUBLISHED);
        guideRepository.save(guide);
    }

    /**
     * 属主校验：仅作者本人或 ADMIN 可操作该攻略。
     */
    private void ensureOwnerOrAdmin(Guide guide, Long operatorId) {
        boolean isAdmin = com.gametips.platform.common.security.CurrentUser.hasRole("ADMIN");
        if (!isAdmin && !guide.getAuthorId().equals(operatorId)) {
            throw new BizException(ErrorCodes.FORBIDDEN, "只能操作自己的攻略");
        }
    }

    /**
     * 作者更新攻略时，将旧内容写入版本历史快照（用于 diff）。
     */
    @org.springframework.cache.annotation.CacheEvict(cacheNames = "guide:detail", key = "#id")
    @Transactional
    public Guide updateWithSnapshot(Long id, Guide update, Long operatorId) {
        Guide guide = get(id);
        ensureOwnerOrAdmin(guide, operatorId);
        snapshot(guide);
        guide.setTitle(update.getTitle());
        guide.setSummary(update.getSummary());
        guide.setContent(update.getContent());
        guide.setTags(update.getTags());
        guide.setDifficulty(update.getDifficulty());
        guide.setVersionId(update.getVersionId());
        if (guide.getStatus() == GuideStatus.PENDING_VERIFICATION) {
            guide.setStatus(GuideStatus.PUBLISHED);
        }
        guide = guideRepository.save(guide);
        syncIndex(guide);
        return guide;
    }

    @Transactional
    public Guide delete(Long id, Long operatorId) {
        Guide guide = get(id);
        ensureOwnerOrAdmin(guide, operatorId);
        guide.setStatus(GuideStatus.ARCHIVED);
        guide = guideRepository.save(guide);
        removeIndex(guide.getId());
        return guide;
    }

    /**
     * ES 启用时将攻略同步到索引；PG 模式下无该 Bean，静默跳过。
     */
    private void syncIndex(Guide guide) {
        guideIndexProvider.ifAvailable(s -> s.index(guide));
    }

    private void removeIndex(Long id) {
        guideIndexProvider.ifAvailable(s -> s.delete(id));
    }

    /**
     * 克隆攻略用于新版本（内容复制，状态置草稿）。
     */
    @Transactional
    public Guide cloneForVersion(Long id, Long newVersionId, Long operatorId) {
        Guide source = get(id);
        ensureOwnerOrAdmin(source, operatorId);
        Guide clone = new Guide();
        clone.setGameId(source.getGameId());
        clone.setVersionId(newVersionId);
        clone.setTitle(source.getTitle() + "（新版本）");
        clone.setAuthorId(source.getAuthorId());
        clone.setType(source.getType());
        clone.setDifficulty(source.getDifficulty());
        clone.setTags(source.getTags());
        clone.setSummary(source.getSummary());
        clone.setContent(source.getContent());
        clone.setStatus(GuideStatus.DRAFT);
        return guideRepository.save(clone);
    }

    public List<GuideVersionHistory> versionHistory(Long guideId) {
        return historyRepository.findByGuideIdOrderByUpdatedAtDesc(guideId);
    }

    /**
     * 版本差分：对比两个版本快照的内容步骤。
     * 简单实现：返回 from/to 的步骤数及标题列表差异；结构化字段级 diff 可后续增强。
     */
    public Map<String, Object> diff(Long guideId, Long fromVersionId, Long toVersionId) {
        GuideVersionHistory from = historyRepository
                .findTopByGuideIdAndVersionIdOrderByUpdatedAtDesc(guideId, fromVersionId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "版本快照不存在"));
        GuideVersionHistory to = historyRepository
                .findTopByGuideIdAndVersionIdOrderByUpdatedAtDesc(guideId, toVersionId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "版本快照不存在"));
        return Map.of(
                "from", from.getContentSnapshot(),
                "to", to.getContentSnapshot());
    }

    private void snapshot(Guide guide) {
        GuideVersionHistory h = new GuideVersionHistory();
        h.setGuideId(guide.getId());
        h.setVersionId(guide.getVersionId());
        h.setContentSnapshot(guide.getContent());
        h.setUpdatedBy(guide.getAuthorId());
        historyRepository.save(h);
    }

    public Page<Guide> listByGame(Long gameId, GuideStatus status, int page, int size) {
        if (gameId == null) {
            return guideRepository.findByStatusOrderByCreatedAtDesc(status, PageRequest.of(page, size));
        }
        return guideRepository.findByGameIdAndStatusOrderByCreatedAtDesc(gameId, status, PageRequest.of(page, size));
    }
}
