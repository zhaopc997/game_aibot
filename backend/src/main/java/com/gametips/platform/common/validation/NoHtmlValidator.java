package com.gametips.platform.common.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.regex.Pattern;

/**
 * 纯文本校验实现。
 *
 * <p>判定规则：出现形如 {@code <tag>}、{@code </tag>}、{@code <tag/>} 的片段即拒绝。
 * 单独出现的 {@code <}（如「血量 <100」）不拦截，避免误伤正常内容。
 *
 * <p>同时拦截常见的脚本伪协议（{@code javascript:}、{@code data:text/html}），
 * 它们即便不带标签也能在链接场景下触发执行。
 */
public class NoHtmlValidator implements ConstraintValidator<NoHtml, String> {

    /** 标签起始：< 后紧跟字母或 / 字母 */
    private static final Pattern TAG = Pattern.compile("<\\s*/?\\s*[a-zA-Z][^>]*>");

    /** 脚本伪协议 */
    private static final Pattern SCHEME = Pattern.compile(
            "(?i)\\b(?:javascript|vbscript)\\s*:|data\\s*:\\s*text/html");

    @Override
    public boolean isValid(String value, ConstraintValidatorContext ctx) {
        if (value == null || value.isEmpty()) {
            return true;
        }
        if (SCHEME.matcher(value).find()) {
            return false;
        }
        return !TAG.matcher(value).find();
    }
}
