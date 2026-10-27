package com.gametips.platform.common.api;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.FieldError;
import org.springframework.web.HttpMediaTypeNotSupportedException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

/**
 * 全局异常处理。
 *
 * <h3>状态码语义</h3>
 * 初版只有 BizException / AccessDenied / 参数校验 / 兜底 500 四类，
 * 导致「路径不存在」「方法不支持」「参数类型错」全部落到兜底分支返回 500。
 * 后果有两个：
 * <ul>
 *   <li>语义错误 —— 500 表示「服务端故障」，而这些是客户端问题，会误导排障；</li>
 *   <li>淹没告警 —— 大量伪 500 会掩盖真实故障，监控形同虚设。</li>
 * </ul>
 * 这里按 HTTP 语义逐一归类，兜底 500 只保留给真正未预期的异常。
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizException.class)
    public ResponseEntity<ApiResponse<Void>> handleBiz(BizException e) {
        HttpStatus status = switch (e.getCode()) {
            case ErrorCodes.UNAUTHORIZED -> HttpStatus.UNAUTHORIZED;
            case ErrorCodes.FORBIDDEN -> HttpStatus.FORBIDDEN;
            case ErrorCodes.NOT_FOUND -> HttpStatus.NOT_FOUND;
            case ErrorCodes.CONFLICT -> HttpStatus.CONFLICT;
            case ErrorCodes.RATE_LIMITED -> HttpStatus.TOO_MANY_REQUESTS;
            default -> HttpStatus.BAD_REQUEST;
        };
        return ResponseEntity.status(status).body(ApiResponse.error(e.getCode(), e.getMessage()));
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ApiResponse<Void>> handleAccessDenied(AccessDeniedException e) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(ApiResponse.error(ErrorCodes.FORBIDDEN, "无权限"));
    }

    /** 参数校验失败（@Valid） → 400 */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleValidation(MethodArgumentNotValidException e) {
        FieldError fe = e.getBindingResult().getFieldError();
        String msg = fe == null ? "参数错误" : fe.getField() + " " + fe.getDefaultMessage();
        return ApiResponse.error(ErrorCodes.PARAM_ERROR, msg);
    }

    /**
     * 路径/查询参数类型不匹配，如 /guides/abc、?size=xyz → 400
     * （原先落到兜底分支返回 500）
     */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleTypeMismatch(MethodArgumentTypeMismatchException e) {
        String name = e.getName();
        Class<?> required = e.getRequiredType();
        String expect = required == null ? "" : "，应为 " + required.getSimpleName();
        return ApiResponse.error(ErrorCodes.PARAM_ERROR, "参数 " + name + " 格式不正确" + expect);
    }

    /** 请求体解析失败（JSON 格式错、字段类型不符） → 400 */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleUnreadable(HttpMessageNotReadableException e) {
        return ApiResponse.error(ErrorCodes.PARAM_ERROR, "请求体格式不正确");
    }

    /** HTTP 方法不支持 → 405，并带 Allow 头 */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<ApiResponse<Void>> handleMethodNotSupported(
            HttpRequestMethodNotSupportedException e) {
        ResponseEntity.BodyBuilder b = ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED);
        if (e.getSupportedHttpMethods() != null) {
            b.allow(e.getSupportedHttpMethods().toArray(new org.springframework.http.HttpMethod[0]));
        }
        return b.body(ApiResponse.error(ErrorCodes.PARAM_ERROR,
                "该接口不支持 " + e.getMethod() + " 方法"));
    }

    /** Content-Type 不支持 → 415 */
    @ExceptionHandler(HttpMediaTypeNotSupportedException.class)
    @ResponseStatus(HttpStatus.UNSUPPORTED_MEDIA_TYPE)
    public ApiResponse<Void> handleMediaType(HttpMediaTypeNotSupportedException e) {
        return ApiResponse.error(ErrorCodes.PARAM_ERROR, "不支持的 Content-Type");
    }

    /**
     * 路径不存在 → 404。
     *
     * <p>Spring 6.1 起，未匹配到任何 handler 的请求会抛 NoResourceFoundException，
     * 初版没有单独处理，于是「功能未实现的接口」全都返回 500。
     */
    @ExceptionHandler(NoResourceFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiResponse<Void> handleNoResource(NoResourceFoundException e) {
        return ApiResponse.error(ErrorCodes.NOT_FOUND, "接口不存在");
    }

    /** 真正的未预期异常才返回 500 */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse<Void> handleUnknown(Exception e) {
        log.error("unhandled exception", e);
        return ApiResponse.error(ErrorCodes.INTERNAL_ERROR, "系统繁忙，请稍后再试");
    }
}
