package com.gametips.platform.module.content.repository;

import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface GuideRepository extends JpaRepository<Guide, Long> {

    Page<Guide> findByGameIdAndStatusOrderByCreatedAtDesc(Long gameId, GuideStatus status, Pageable pageable);

    Page<Guide> findByStatusOrderByCreatedAtDesc(GuideStatus status, Pageable pageable);

    List<Guide> findTop100ByStatusInOrderByUpdatedAtDesc(java.util.Collection<GuideStatus> statuses);

    List<Guide> findByGameIdAndStatus(Long gameId, GuideStatus status);

    List<Guide> findTop10ByGameIdAndStatusOrderByUpdatedAtDesc(Long gameId, GuideStatus status);

    List<Guide> findTop3ByStatusOrderByUpdatedAtDesc(GuideStatus status);

    long countByGameIdAndStatus(Long gameId, GuideStatus status);

    /**
     * 简易搜索：标题/摘要 ILIKE + 标签(jsonb 包含) + 状态过滤。
     * MVP 使用 PG 原生 jsonb 查询；数据量增长后迁移 Elasticsearch。
     */
    @Query(value = """
            SELECT * FROM guide g
            WHERE g.status = :status
              AND (:gameId IS NULL OR g.game_id = :gameId)
              AND (:keyword IS NULL OR :keyword = ''
                   OR LOWER(g.title) LIKE LOWER(CONCAT('%', :keyword, '%'))
                   OR LOWER(g.summary) LIKE LOWER(CONCAT('%', :keyword, '%')))
              AND (:tag IS NULL OR :tag = '' OR jsonb_exists(g.tags::jsonb, :tag))
            ORDER BY g.updated_at DESC
            """,
           countQuery = """
            SELECT count(*) FROM guide g
            WHERE g.status = :status
              AND (:gameId IS NULL OR g.game_id = :gameId)
              AND (:keyword IS NULL OR :keyword = ''
                   OR LOWER(g.title) LIKE LOWER(CONCAT('%', :keyword, '%'))
                   OR LOWER(g.summary) LIKE LOWER(CONCAT('%', :keyword, '%')))
              AND (:tag IS NULL OR :tag = '' OR jsonb_exists(g.tags::jsonb, :tag))
            """,
           nativeQuery = true)
    Page<Guide> search(@Param("keyword") String keyword,
                       @Param("tag") String tag,
                       @Param("gameId") Long gameId,
                       @Param("status") String status,
                       Pageable pageable);

    @org.springframework.data.jpa.repository.Modifying
    @Query("UPDATE Guide g SET g.likeCount = coalesce(g.likeCount, 0) + 1 WHERE g.id = :id")
    void incrementLikeCount(@Param("id") Long id);

    @org.springframework.data.jpa.repository.Modifying
    @Query("UPDATE Guide g SET g.likeCount = CASE WHEN coalesce(g.likeCount, 0) > 0 THEN g.likeCount - 1 ELSE 0 END WHERE g.id = :id")
    void decrementLikeCount(@Param("id") Long id);
}
