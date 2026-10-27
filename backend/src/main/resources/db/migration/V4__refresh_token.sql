-- ============================================================
-- V4: Refresh Token 服务端存储（支持轮换、复用检测、主动吊销）
--
-- 背景：原实现 refresh 接口只校验 JWT 签名就签发新令牌，
-- 服务端不记录任何状态，导致：
--   1) 同一 Refresh Token 可以无限次换取新令牌（无轮换）；
--   2) 令牌泄露后无法吊销，用户也无法主动登出；
--   3) 无法检测令牌是否已被他人复用。
--
-- 设计：
--   · 只存 token 的 SHA-256 摘要，不存原文 —— 即使库被读也无法直接冒用；
--   · 每次刷新把旧记录标记 revoked_at 并写入 replaced_by（链式追溯）；
--   · 若已被吊销的 token 再次出现 → 判定为复用/泄露，吊销该用户全部令牌；
--   · 过期记录由定时任务清理，避免表无限增长。
-- ============================================================

BEGIN;

CREATE TABLE refresh_token (
    id           BIGSERIAL PRIMARY KEY,
    user_id      BIGINT       NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    -- JWT 原文的 sha256 十六进制摘要（64 字符）
    token_hash   VARCHAR(64)  NOT NULL,
    issued_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    expires_at   TIMESTAMPTZ  NOT NULL,
    -- 非空表示已被轮换或吊销，不再可用于刷新
    revoked_at   TIMESTAMPTZ,
    -- 轮换后的后继令牌摘要，用于追溯令牌链
    replaced_by  VARCHAR(64),
    -- 便于「查看登录设备」与异常登录告警（后续功能）
    client_ip    VARCHAR(64),
    user_agent   VARCHAR(255)
);

-- 刷新时按摘要精确查找，必须唯一
CREATE UNIQUE INDEX uq_refresh_token_hash ON refresh_token (token_hash);
CREATE INDEX idx_refresh_token_user ON refresh_token (user_id);
-- 清理过期记录用
CREATE INDEX idx_refresh_token_expires ON refresh_token (expires_at);

COMMENT ON TABLE refresh_token IS 'Refresh Token 存储（仅摘要），支持轮换与吊销';

COMMIT;
