package com.gametips.platform.common.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 密码强度校验。
 *
 * <p>原实现只校验长度 6–128，实测 {@code 12345678} 可直接注册成功。
 * 配合「无失败锁定」，弱口令喷洒的成功率极高。
 */
@Documented
@Constraint(validatedBy = StrongPasswordValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface StrongPassword {

    String message() default "密码至少 8 位，且需同时包含字母和数字";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
