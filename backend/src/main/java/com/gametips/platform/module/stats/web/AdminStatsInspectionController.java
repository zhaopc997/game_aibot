package com.gametips.platform.module.stats.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.api.PageResult;
import com.gametips.platform.module.stats.domain.StatVersionAudit;
import com.gametips.platform.module.stats.service.StatInspectionService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/admin/stats")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ADMIN')")
public class AdminStatsInspectionController {

    private final StatInspectionService inspectionService;

    @GetMapping("/audit-logs")
    public ApiResponse<PageResult<StatVersionAudit>> listAuditLogs(
            @RequestParam(defaultValue = "2") Long gameId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<StatVersionAudit> result = inspectionService.listAudits(gameId, status, PageRequest.of(page, size));
        return ApiResponse.ok(PageResult.of(result.getContent(), result.hasNext() ? String.valueOf(page + 1) : null));
    }

    @PostMapping("/inspect")
    public ApiResponse<Map<String, Object>> runInspection(
            @RequestParam(defaultValue = "2") Long gameId) {
        Map<String, Object> result = inspectionService.inspectGameStats(gameId);
        return ApiResponse.ok(result);
    }
}
