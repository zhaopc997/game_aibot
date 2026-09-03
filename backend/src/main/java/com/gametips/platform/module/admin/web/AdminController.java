package com.gametips.platform.module.admin.web;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.api.PageResult;
import com.gametips.platform.module.admin.service.AdminService;
import com.gametips.platform.module.user.domain.User;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/admin")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    private final AdminService adminService;

    @GetMapping("/users")
    public ApiResponse<PageResult<User>> listUsers(@RequestParam(defaultValue = "0") int page,
                                                   @RequestParam(defaultValue = "20") int size) {
        Page<User> result = adminService.listUsers(page, size);
        return ApiResponse.ok(PageResult.of(result.getContent(),
                result.hasNext() ? String.valueOf(page + 1) : null));
    }

    @PutMapping("/users/{id}/status")
    public ApiResponse<User> changeStatus(@PathVariable Long id, @RequestBody Map<String, String> body) {
        return ApiResponse.ok(adminService.changeUserStatus(id, body.get("status")));
    }
}
