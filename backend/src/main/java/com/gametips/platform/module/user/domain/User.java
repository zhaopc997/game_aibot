package com.gametips.platform.module.user.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.gametips.platform.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "\"user\"")
public class User extends BaseEntity {

    @Column(name = "username", nullable = false, length = 64)
    private String username;

    @Column(name = "email", nullable = false, length = 128)
    private String email;

    @JsonIgnore
    @Column(name = "password_hash", nullable = false, length = 255)
    private String passwordHash;

    @Column(name = "avatar", length = 500)
    private String avatar;

    @Column(name = "bio")
    private String bio;

    @Column(name = "level", nullable = false)
    private Integer level = 1;

    @Column(name = "exp", nullable = false)
    private Long exp = 0L;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 32)
    private UserStatus status = UserStatus.NORMAL;
}
