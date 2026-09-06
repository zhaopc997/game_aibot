package com.gametips.platform.module.tool.annotation;

/**
 * Tool 风险等级(V2 architecture §4.3 安全约束)。
 *
 * <ul>
 *   <li>{@link #READ_ONLY} 仅读取,无副作用</li>
 *   <li>{@link #WRITE} 会修改状态,需用户在 Plan 中显式确认</li>
 *   <li>{@link #DESTRUCTIVE} 不可逆操作,需二次确认 + 审计</li>
 * </ul>
 */
public enum RiskLevel {
    READ_ONLY,
    WRITE,
    DESTRUCTIVE
}
