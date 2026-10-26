package com.gametips.platform.module.community.service;

import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import com.gametips.platform.module.community.domain.Answer;
import com.gametips.platform.module.community.domain.Favorite;
import com.gametips.platform.module.community.domain.Like;
import com.gametips.platform.module.community.domain.Question;
import com.gametips.platform.module.community.domain.Report;
import com.gametips.platform.module.community.repository.AnswerRepository;
import com.gametips.platform.module.community.repository.FavoriteRepository;
import com.gametips.platform.module.community.repository.LikeRepository;
import com.gametips.platform.module.community.repository.QuestionRepository;
import com.gametips.platform.module.community.repository.ReportRepository;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.notification.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CommunityService {

    private final LikeRepository likeRepository;
    private final FavoriteRepository favoriteRepository;
    private final QuestionRepository questionRepository;
    private final AnswerRepository answerRepository;
    private final ReportRepository reportRepository;
    private final GuideRepository guideRepository;
    private final NotificationService notificationService;

    // ---------- 点赞 ----------

    @Transactional
    public boolean toggleLike(String targetType, Long targetId, Long userId) {
        return likeRepository.findByTargetTypeAndTargetIdAndUserId(targetType, targetId, userId)
                .map(like -> {
                    likeRepository.delete(like);
                    if ("guide".equalsIgnoreCase(targetType)) {
                        guideRepository.decrementLikeCount(targetId);
                    }
                    return false;
                })
                .orElseGet(() -> {
                    Like like = new Like();
                    like.setTargetType(targetType);
                    like.setTargetId(targetId);
                    like.setUserId(userId);
                    likeRepository.save(like);
                    if ("guide".equalsIgnoreCase(targetType)) {
                        guideRepository.incrementLikeCount(targetId);
                        guideRepository.findById(targetId).ifPresent(g -> {
                            if (!g.getAuthorId().equals(userId)) {
                                notificationService.create(g.getAuthorId(), "LIKE", "收到新的点赞",
                                        "你的攻略《" + g.getTitle() + "》收到了一个赞", "guide", targetId);
                            }
                        });
                    }
                    return true;
                });
    }

    public long likeCount(String targetType, Long targetId) {
        return likeRepository.countByTargetTypeAndTargetId(targetType, targetId);
    }

    // ---------- 收藏 ----------

    @Transactional
    public boolean toggleFavorite(String targetType, Long targetId, Long userId) {
        return favoriteRepository.findByTargetTypeAndTargetIdAndUserId(targetType, targetId, userId)
                .map(fav -> {
                    favoriteRepository.delete(fav);
                    return false;
                })
                .orElseGet(() -> {
                    Favorite fav = new Favorite();
                    fav.setTargetType(targetType);
                    fav.setTargetId(targetId);
                    fav.setUserId(userId);
                    favoriteRepository.save(fav);
                    return true;
                });
    }

    public List<Favorite> myFavorites(Long userId) {
        return favoriteRepository.findTop50ByUserIdOrderByCreatedAtDesc(userId);
    }

    // ---------- 问答 ----------

    @Transactional
    public Question createQuestion(Question q) {
        q.setId(null);
        return questionRepository.save(q);
    }

    public List<Question> questions(Long gameId) {
        // gameId 为空表示"全站最新"，必须走不带 game_id 条件的查询：
        // 传 null 给 findByGameId... 会生成 game_id = NULL，SQL 中恒为 false。
        return gameId == null
                ? questionRepository.findTop50ByOrderByCreatedAtDesc()
                : questionRepository.findTop50ByGameIdOrderByCreatedAtDesc(gameId);
    }

    public Question getQuestion(Long questionId) {
        return questionRepository.findById(questionId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "问题不存在"));
    }

    @Transactional
    public Answer answer(Long questionId, Answer a) {
        Question q = questionRepository.findById(questionId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "问题不存在"));
        a.setId(null);
        a.setQuestionId(q.getId());
        return answerRepository.save(a);
    }

    public List<Answer> answers(Long questionId) {
        return answerRepository.findByQuestionIdOrderByCreatedAtAsc(questionId);
    }

    @Transactional
    public void acceptAnswer(Long questionId, Long answerId, Long userId) {
        Question q = questionRepository.findById(questionId)
                .orElseThrow(() -> new BizException(ErrorCodes.NOT_FOUND, "问题不存在"));
        if (!q.getUserId().equals(userId)) {
            throw new BizException(ErrorCodes.FORBIDDEN, "只有提问者可以采纳答案");
        }
        q.setAcceptedAnswerId(answerId);
        q.setStatus("SOLVED");
        questionRepository.save(q);
    }

    // ---------- 举报 ----------

    @Transactional
    public Report report(Report r) {
        r.setId(null);
        return reportRepository.save(r);
    }

    public List<Report> reportQueue() {
        return reportRepository.findTop100ByStatusOrderByCreatedAtAsc("PENDING");
    }
}
