package com.gametips.platform.common.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 纯文本字段校验：拒绝包含 HTML/脚本标签的输入。
 *
 * <p>用于标题、描述、评论这类<b>本就应当只有纯文本</b>的字段。
 * 前端目前用 React JSX 渲染会自动转义，所以不存在可利用的 XSS；
 * 但服务端不设防意味着存量脏数据会在将来某次前端改造
 * （比如引入富文本编辑器或 dangerouslySetInnerHTML）时立刻变成存储型 XSS。
 *
 * <p>做法是「拒收」而不是「清洗」：静默剥标签会让用户以为提交成功了，
 * 实际内容被改得面目全非；直接报错更清晰。
 */
@Documented
@Constraint(validatedBy = NoHtmlValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface NoHtml {

    String message() default "内容不能包含 HTML 标签";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
