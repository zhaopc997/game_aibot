package com.gametips.platform.module.user.repository;

import com.gametips.platform.module.user.domain.Role;
import com.gametips.platform.module.user.domain.UserRole;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UserRoleRepository extends JpaRepository<UserRole, Long> {

    List<UserRole> findByUserId(Long userId);

    boolean existsByUserIdAndRole(Long userId, Role role);
}
