package com.gametips.platform.common.api;

/**
 * 业务错误码。
 * 0 成功；1xxx 参数/认证；2xxx 资源；3xxx 限流。
 */
public final class ErrorCodes {

    private ErrorCodes() {}

    public static final int PARAM_ERROR = 1001;
    public static final int UNAUTHORIZED = 1002;
    public static final int FORBIDDEN = 1003;
    public static final int NOT_FOUND = 2001;
    public static final int CONFLICT = 2002;
    public static final int RATE_LIMITED = 3001;
    public static final int INTERNAL_ERROR = 5000;
}
