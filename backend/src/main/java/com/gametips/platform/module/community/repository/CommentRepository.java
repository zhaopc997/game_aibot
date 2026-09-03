package com.gametips.platform.module.community.repository;

import com.gametips.platform.module.community.domain.Comment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CommentRepository extends JpaRepository<Comment, Long> {

    List<Comment> findTop20ByTargetTypeAndTargetIdAndStatusOrderByCreatedAtDesc(
            String targetType, Long targetId, String status);
}
