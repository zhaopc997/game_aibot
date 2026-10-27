package com.gametips.platform.module.community.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.community.domain.Answer;
import com.gametips.platform.module.community.domain.Favorite;
import com.gametips.platform.module.community.domain.Question;
import com.gametips.platform.module.community.domain.Report;
import com.gametips.platform.module.community.service.CommunityService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class CommunityController {

    private final CommunityService communityService;

    // ---------- 点赞 ----------

    @PostMapping("/likes")
    public ApiResponse<Map<String, Object>> toggleLike(@RequestParam String targetType,
                                                       @RequestParam Long targetId) {
        boolean liked = communityService.toggleLike(targetType, targetId, CurrentUser.userId());
        return ApiResponse.ok(Map.of("liked", liked, "count", communityService.likeCount(targetType, targetId)));
    }

    // ---------- 收藏 ----------

    @PostMapping("/favorites")
    public ApiResponse<Map<String, Boolean>> toggleFavorite(@RequestParam String targetType,
                                                            @RequestParam Long targetId) {
        return ApiResponse.ok(Map.of("favorited",
                communityService.toggleFavorite(targetType, targetId, CurrentUser.userId())));
    }

    @GetMapping("/favorites/mine")
    public ApiResponse<List<Favorite>> myFavorites() {
        return ApiResponse.ok(communityService.myFavorites(CurrentUser.userId()));
    }

    // ---------- 问答 ----------

    @GetMapping("/questions")
    public ApiResponse<List<Question>> questions(@RequestParam(required = false) Long gameId) {
        return ApiResponse.ok(communityService.questions(gameId));
    }

    @GetMapping("/questions/{questionId}")
    public ApiResponse<Question> question(@PathVariable Long questionId) {
        return ApiResponse.ok(communityService.getQuestion(questionId));
    }

    @PostMapping("/questions")
    public ApiResponse<Question> createQuestion(@jakarta.validation.Valid @RequestBody Question q) {
        q.setUserId(CurrentUser.userId());
        return ApiResponse.ok(communityService.createQuestion(q));
    }

    @GetMapping("/questions/{questionId}/answers")
    public ApiResponse<List<Answer>> answers(@PathVariable Long questionId) {
        return ApiResponse.ok(communityService.answers(questionId));
    }

    @PostMapping("/questions/{questionId}/answers")
    public ApiResponse<Answer> answer(@PathVariable Long questionId, @RequestBody Answer a) {
        a.setUserId(CurrentUser.userId());
        return ApiResponse.ok(communityService.answer(questionId, a));
    }

    @PostMapping("/questions/{questionId}/accept-answer")
    public ApiResponse<Void> acceptAnswer(@PathVariable Long questionId, @RequestParam Long answerId) {
        communityService.acceptAnswer(questionId, answerId, CurrentUser.userId());
        return ApiResponse.ok();
    }

    // ---------- 举报 ----------

    @PostMapping("/reports")
    public ApiResponse<Report> report(@RequestBody Report r) {
        r.setReporterId(CurrentUser.userId());
        return ApiResponse.ok(communityService.report(r));
    }

    @PreAuthorize("hasAnyRole('MODERATOR','ADMIN')")
    @GetMapping("/reports/queue")
    public ApiResponse<List<Report>> reportQueue() {
        return ApiResponse.ok(communityService.reportQueue());
    }
}
