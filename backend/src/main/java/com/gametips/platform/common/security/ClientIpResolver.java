package com.gametips.platform.common.security;

import jakarta.servlet.http.HttpServletRequest;

/**
 * 真实客户端 IP 解析。
 *
 * <h3>为什么要单独抽出来</h3>
 * 本站的实际链路是：
 * <pre>
 *   浏览器 → Caddy(443) → 前端 nginx(8088) → 后端(8080)
 * </pre>
 * 两跳都在内网，因此后端拿到的 {@code getRemoteAddr()} 永远是 Docker 网关地址
 * （实测 172.19.0.1）。更麻烦的是前端 nginx 里有
 * {@code proxy_set_header X-Real-IP $remote_addr}，会把 Caddy 传下来的真实 IP
 * <b>覆盖成网关地址</b>。
 *
 * <p>如果限流按这个地址计数，所有用户会共用同一个配额 ——
 * 一个人触发限流就会把全站用户一起挡在门外，这比不限流更糟。
 *
 * <h3>为什么优先取 X-Forwarded-For 的第一跳</h3>
 * Caddy 的 reverse_proxy 会把 {@code X-Forwarded-For} <b>整体替换</b>为真实客户端 IP
 * （而不是在客户端提供的值后面追加），因此第一跳是可信的；
 * nginx 再用 {@code $proxy_add_x_forwarded_for} 追加自己的地址，
 * 于是这个头形如 {@code 真实IP, 网关IP}。取第一个即可。
 *
 * <p>若请求不经过 Caddy（例如同机调试），退回到 {@code X-Real-IP} 与 socket 地址，
 * 并跳过内网/回环地址，避免再次把网关地址当成用户身份。
 */
public final class ClientIpResolver {

    private ClientIpResolver() {
    }

    public static String resolve(HttpServletRequest request) {
        // 1) X-Forwarded-For 的第一跳（Caddy 已净化为真实客户端 IP）
        String xff = request.getHeader("X-Forwarded-For");
        if (xff != null && !xff.isBlank()) {
            String first = xff.split(",")[0].trim();
            if (!first.isEmpty() && !isInternal(first)) {
                return first;
            }
        }

        // 2) X-Real-IP（仅在不是内网地址时采信）
        String real = request.getHeader("X-Real-IP");
        if (real != null && !real.isBlank() && !isInternal(real.trim())) {
            return real.trim();
        }

        // 3) 兜底：socket 地址（此时通常是网关，仅用于日志/计数不崩）
        String remote = request.getRemoteAddr();
        return (remote == null || remote.isBlank()) ? "unknown" : remote;
    }

    /** 回环与私有网段：这些地址不能代表真实用户 */
    static boolean isInternal(String ip) {
        if (ip == null || ip.isEmpty()) {
            return true;
        }
        String s = ip.toLowerCase();
        if (s.equals("localhost") || s.startsWith("127.") || s.equals("::1") || s.equals("0:0:0:0:0:0:0:1")) {
            return true;
        }
        if (s.startsWith("10.") || s.startsWith("192.168.")) {
            return true;
        }
        // 172.16.0.0 – 172.31.255.255
        if (s.startsWith("172.")) {
            String[] parts = s.split("\\.");
            if (parts.length > 1) {
                try {
                    int second = Integer.parseInt(parts[1]);
                    return second >= 16 && second <= 31;
                } catch (NumberFormatException ignored) {
                    return false;
                }
            }
        }
        return false;
    }
}
