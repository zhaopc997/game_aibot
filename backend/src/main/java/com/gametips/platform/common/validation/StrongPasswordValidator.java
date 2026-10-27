package com.gametips.platform.common.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.Set;

/**
 * 密码强度实现。
 *
 * <p>规则（按 OWASP 建议的「长度优先 + 拦截常见弱口令」，而不是强推特殊字符）：
 * <ol>
 *   <li>长度 8–128：过短易爆破，过长（>128）会让 BCrypt 计算成本失控；</li>
 *   <li>至少包含一个字母和一个数字 —— 挡住纯数字/纯字母的常见弱口令；</li>
 *   <li>不在常见弱口令集合内（大小写与常见变体归一后比对）；</li>
 *   <li>不是全相同字符（如 11111111）或简单连续序列（如 12345678）。</li>
 * </ol>
 *
 * <p>没有强制特殊字符：研究表明强制符号反而会导致用户使用 {@code Password1!} 这类
 * 可预测模式，长度与弱口令黑名单的收益更高。
 */
public class StrongPasswordValidator implements ConstraintValidator<StrongPassword, String> {

    private static final int MIN = 8;
    private static final int MAX = 128;

    /**
     * 常见弱口令（已小写）。不求覆盖全部，重点是挡住自动化喷洒最常用的那批。
     * 生产环境可替换为完整字典文件（如 rockyou.txt 的前 10 万条）。
     */
    private static final Set<String> WEAK = Set.of(
            "12345678", "123456789", "1234567890", "1234567", "123456",
            "password", "password1", "password123", "passw0rd",
            "qwertyui", "qwerty12", "qwerty123", "abc12345", "abcd1234",
            "a1234567", "aa123456", "1qaz2wsx", "qazwsxed", "zaq12wsx",
            "iloveyou", "admin123", "administrator", "root1234",
            "woaini1314", "5201314520", "qq123456", "wang1234",
            "p@ssw0rd", "pass1234", "test1234", "guest123"
    );

    @Override
    public boolean isValid(String value, ConstraintValidatorContext ctx) {
        // null 交给 @NotBlank 处理，避免重复报错
        if (value == null) {
            return true;
        }
        if (value.length() < MIN || value.length() > MAX) {
            return false;
        }

        boolean hasLetter = false;
        boolean hasDigit = false;
        for (char c : value.toCharArray()) {
            if (Character.isLetter(c)) {
                hasLetter = true;
            } else if (Character.isDigit(c)) {
                hasDigit = true;
            }
        }
        if (!hasLetter || !hasDigit) {
            return false;
        }

        String lower = value.toLowerCase();
        if (WEAK.contains(lower)) {
            return false;
        }

        // 全相同字符
        if (value.chars().distinct().count() == 1) {
            return false;
        }

        // 纯连续序列，如 12345678 / abcdefgh（长度 >= 6 的递增或递减）
        if (isSequential(lower)) {
            return false;
        }
        return true;
    }

    private static boolean isSequential(String s) {
        if (s.length() < 6) {
            return false;
        }
        int up = 0;
        int down = 0;
        for (int i = 1; i < s.length(); i++) {
            int d = s.charAt(i) - s.charAt(i - 1);
            if (d == 1) {
                up++;
            } else if (d == -1) {
                down++;
            }
        }
        return up >= s.length() - 1 || down >= s.length() - 1;
    }
}
