package com.gametips.platform.module.audit.repository;

import com.gametips.platform.module.audit.domain.AuditLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {

    List<AuditLog> findTop50ByOperatorIdOrderByCreatedAtDesc(Long operatorId);

    List<AuditLog> findTop50ByTargetTypeAndTargetIdOrderByCreatedAtDesc(String targetType, Long targetId);
}
