package com.gametips.platform.common.api;

import lombok.Data;

import java.util.List;

/**
 * 游标分页结果。
 * nextCursor 为 null 表示没有更多数据。
 */
@Data
public class PageResult<T> {

    private List<T> items;
    private String nextCursor;

    public static <T> PageResult<T> of(List<T> items, String nextCursor) {
        PageResult<T> r = new PageResult<>();
        r.items = items;
        r.nextCursor = nextCursor;
        return r;
    }
}
