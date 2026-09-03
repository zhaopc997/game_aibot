package com.gametips.platform.module.review.repository;

import com.gametips.platform.module.review.domain.ContentReview;
import com.gametips.platform.module.review.domain.ReviewStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ContentReviewRepository extends JpaRepository<ContentReview, Long> {

    List<ContentReview> findTop100ByStatusOrderByCreatedAtAsc(ReviewStatus status);
}
