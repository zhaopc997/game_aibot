package com.gametips.platform.module.community.repository;

import com.gametips.platform.module.community.domain.Report;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ReportRepository extends JpaRepository<Report, Long> {

    List<Report> findTop100ByStatusOrderByCreatedAtAsc(String status);
}
