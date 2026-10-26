package com.gametips.platform.module.stats.repository;

import com.gametips.platform.module.stats.domain.StatVersionAudit;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StatVersionAuditRepository extends JpaRepository<StatVersionAudit, Long> {

    List<StatVersionAudit> findByCheckBatchNo(String checkBatchNo);

    Page<StatVersionAudit> findByGameIdOrderByCheckedAtDesc(Long gameId, Pageable pageable);

    Page<StatVersionAudit> findByGameIdAndStatusOrderByCheckedAtDesc(Long gameId, String status, Pageable pageable);
}
