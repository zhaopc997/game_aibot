package com.gametips.platform.module.community.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.module.community.domain.Comment;
import com.gametips.platform.module.community.service.CommentService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/comments")
@RequiredArgsConstructor
public class CommentController {

    private final CommentService commentService;

    @GetMapping
    public ApiResponse<List<Comment>> list(@RequestParam String targetType,
                                           @RequestParam Long targetId) {
        return ApiResponse.ok(commentService.listByTarget(targetType, targetId));
    }

    @PostMapping
    public ApiResponse<Comment> create(@RequestBody Comment comment) {
        comment.setUserId(com.gametips.platform.common.security.CurrentUser.userId());
        comment.setId(null);
        return ApiResponse.ok(commentService.create(comment));
    }
}
