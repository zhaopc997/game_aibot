package com.gametips.platform.module.community.service;

import com.gametips.platform.module.community.domain.Comment;
import com.gametips.platform.module.community.repository.CommentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CommentService {

    private final CommentRepository commentRepository;

    @Transactional
    public Comment create(Comment comment) {
        comment.setId(null);
        return commentRepository.save(comment);
    }

    public List<Comment> listByTarget(String targetType, Long targetId) {
        return commentRepository.findTop20ByTargetTypeAndTargetIdAndStatusOrderByCreatedAtDesc(
                targetType, targetId, "NORMAL");
    }
}
