package com.gametips.platform.module.content.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.api.PageResult;
import com.gametips.platform.common.security.CurrentUser;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.service.GuideService;
import com.gametips.platform.module.content.service.GuideSearchService;
import com.gametips.platform.module.version.domain.GuideVersionHistory;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/guides")
@RequiredArgsConstructor
public class GuideController {

    private final GuideService guideService;
    private final GuideSearchService guideSearchService;

    @PostMapping
    public ApiResponse<Guide> create(@RequestBody Guide guide) {
        guide.setAuthorId(com.gametips.platform.common.security.CurrentUser.userId());
        return ApiResponse.ok(guideService.create(guide));
    }

    @GetMapping("/{id}")
    public ApiResponse<Guide> detail(@PathVariable Long id) {
        return ApiResponse.ok(guideService.get(id));
    }

    @PutMapping("/{id}")
    public ApiResponse<Guide> update(@PathVariable Long id, @RequestBody Guide guide) {
        return ApiResponse.ok(guideService.updateWithSnapshot(id, guide, CurrentUser.userId()));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        guideService.delete(id, CurrentUser.userId());
        return ApiResponse.ok();
    }

    @PostMapping("/{id}/submit-review")
    public ApiResponse<Void> submitReview(@PathVariable Long id) {
        guideService.submitReview(id, CurrentUser.userId());
        return ApiResponse.ok();
    }

    @PostMapping("/{id}/mark-outdated")
    public ApiResponse<Void> markOutdated(@PathVariable Long id) {
        guideService.markOutdated(id, CurrentUser.userId());
        return ApiResponse.ok();
    }

    @PostMapping("/{id}/claim-compatible")
    public ApiResponse<Void> claimCompatible(@PathVariable Long id) {
        guideService.claimCompatible(id, CurrentUser.userId());
        return ApiResponse.ok();
    }

    @GetMapping("/{id}/versions")
    public ApiResponse<List<GuideVersionHistory>> versions(@PathVariable Long id) {
        return ApiResponse.ok(guideService.versionHistory(id));
    }

    @GetMapping("/{id}/diff")
    public ApiResponse<Map<String, Object>> diff(@PathVariable Long id,
                                                 @RequestParam Long from,
                                                 @RequestParam Long to) {
        return ApiResponse.ok(guideService.diff(id, from, to));
    }

    @PostMapping("/{id}/clone")
    public ApiResponse<Guide> clone(@PathVariable Long id, @RequestParam Long versionId) {
        return ApiResponse.ok(guideService.cloneForVersion(id, versionId, CurrentUser.userId()));
    }

    @GetMapping
    public ApiResponse<PageResult<Guide>> list(
            @RequestParam(required = false) Long gameId,
            @RequestParam(defaultValue = "PUBLISHED") GuideStatus status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<Guide> result = guideService.listByGame(gameId, status, page, size);
        return ApiResponse.ok(PageResult.of(result.getContent(),
                result.hasNext() ? String.valueOf(page + 1) : null));
    }

    @GetMapping("/search")
    public ApiResponse<PageResult<Guide>> search(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String tag,
            @RequestParam(required = false) Long gameId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<Guide> result = guideSearchService.search(keyword, tag, gameId, page, size);
        return ApiResponse.ok(PageResult.of(result.getContent(),
                result.hasNext() ? String.valueOf(page + 1) : null));
    }
}
