-- ============================================================
-- V2: OAuth 第三方登录关联表
-- ============================================================

BEGIN;

CREATE TABLE oauth_account (
    id               BIGSERIAL PRIMARY KEY,
    user_id          BIGINT       NOT NULL REFERENCES "user"(id),
    provider         VARCHAR(32)  NOT NULL,          -- GITHUB / STEAM / WECHAT
    external_id      VARCHAR(128) NOT NULL,
    external_username VARCHAR(128),
    avatar_url       VARCHAR(500),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (provider, external_id)
);
CREATE INDEX idx_oauth_user ON oauth_account(user_id);

COMMIT;
