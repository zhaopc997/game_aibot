-- ============================================================
-- 游戏攻略平台 数据库 DDL（PostgreSQL 16）
-- 基于《架构文档-修订版》第4章生成
-- 执行顺序：本文件可直接整份执行（依赖顺序已排好）
-- 约定：
--   * 主键统一 BIGSERIAL（自增）
--   * created_at/updated_at 统一 TIMESTAMPTZ，由触发器维护 updated_at
--   * 软删除统一 deleted_at（NULL 表示未删除）
--   * 长文本用 TEXT，结构化数据用 JSONB
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- 0. 基础函数：updated_at 自动更新触发器
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- 1. 枚举说明
-- 状态/角色字段采用 VARCHAR + CHECK 约束，便于 JPA @Enumerated 映射与 hibernate validate 校验。
-- （不使用 PG 原生 ENUM，避免与 Hibernate 类型校验不兼容）
-- ------------------------------------------------------------

-- ============================================================
-- 2. 用户相关
-- ============================================================

-- 2.1 用户表
CREATE TABLE "user" (
    id            BIGSERIAL PRIMARY KEY,
    username      VARCHAR(64)  NOT NULL,
    email         VARCHAR(128) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar        VARCHAR(500),
    bio           TEXT,
    level         INT          NOT NULL DEFAULT 1,
    exp           BIGINT       NOT NULL DEFAULT 0,
    status        VARCHAR(32)  NOT NULL DEFAULT 'NORMAL',
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at    TIMESTAMPTZ,
    CONSTRAINT chk_user_status CHECK (status IN ('NORMAL', 'DISABLED', 'PENDING_VERIFY'))
);
CREATE UNIQUE INDEX uk_user_username ON "user"(username) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX uk_user_email    ON "user"(email)    WHERE deleted_at IS NULL;

-- 2.2 用户角色表（USER/CREATOR/MODERATOR/ADMIN）
CREATE TABLE user_role (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT      NOT NULL REFERENCES "user"(id),
    role       VARCHAR(32) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, role),
    CONSTRAINT chk_user_role CHECK (role IN ('USER', 'CREATOR', 'MODERATOR', 'ADMIN'))
);

-- 2.3 玩家游戏档案
CREATE TABLE user_game_profile (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT      NOT NULL REFERENCES "user"(id),
    game_id    BIGINT      NOT NULL,              -- FK 见 game 表
    role_info  JSONB       NOT NULL DEFAULT '{}',
    progress   JSONB       NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, game_id)
);

-- 2.4 关注关系
CREATE TABLE follow (
    follower_id BIGINT      NOT NULL REFERENCES "user"(id),
    followee_id BIGINT      NOT NULL REFERENCES "user"(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (follower_id, followee_id)
);

-- 2.5 积分流水
CREATE TABLE user_points_log (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT      NOT NULL REFERENCES "user"(id),
    action     VARCHAR(64) NOT NULL,
    points     INT         NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_points_user ON user_points_log(user_id);

-- ============================================================
-- 3. 内容相关
-- ============================================================

-- 3.1 游戏表
CREATE TABLE game (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    alias           VARCHAR(255),
    platform        VARCHAR(64),
    category        VARCHAR(64),
    cover_url       VARCHAR(500),
    description     TEXT,
    current_version VARCHAR(32),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 3.2 游戏版本
CREATE TABLE game_version (
    id             BIGSERIAL PRIMARY KEY,
    game_id        BIGINT      NOT NULL REFERENCES game(id),
    version_number VARCHAR(32) NOT NULL,
    release_date   DATE,
    patch_notes    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (game_id, version_number)
);

-- 3.3 攻略表（核心表）
CREATE TABLE guide (
    id            BIGSERIAL PRIMARY KEY,
    game_id       BIGINT           NOT NULL REFERENCES game(id),
    version_id    BIGINT           REFERENCES game_version(id),
    title         VARCHAR(255)     NOT NULL,
    author_id     BIGINT           NOT NULL REFERENCES "user"(id),
    type          VARCHAR(32)      NOT NULL DEFAULT 'MANUAL',   -- MANUAL(人工原创) / AI_GENERATED(AI 生成) / CRAWLED(外部采集,须保留署名与来源)
    difficulty    VARCHAR(16),                                  -- EASY / NORMAL / HARD / EXPERT
    tags          JSONB            NOT NULL DEFAULT '[]',
    summary       TEXT,
    content       JSONB            NOT NULL DEFAULT '{"steps":[]}',
    status        VARCHAR(32)  NOT NULL DEFAULT 'DRAFT',
    like_count    BIGINT       NOT NULL DEFAULT 0,
    useful_count  BIGINT       NOT NULL DEFAULT 0,
    verify_count  BIGINT       NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at    TIMESTAMPTZ,
    CONSTRAINT chk_guide_status CHECK (status IN (
        'DRAFT', 'PENDING_REVIEW', 'PUBLISHED',
        'PENDING_VERIFICATION', 'OUTDATED', 'ARCHIVED', 'REJECTED'))
);
CREATE INDEX idx_guide_game_status   ON guide(game_id, status);
CREATE INDEX idx_guide_game_updated  ON guide(game_id, updated_at DESC);
CREATE INDEX idx_guide_author        ON guide(author_id);
CREATE INDEX idx_guide_version       ON guide(version_id);
CREATE INDEX idx_guide_status        ON guide(status);

-- 3.4 攻略版本历史（关联游戏版本的内容快照，用于差分对比）
CREATE TABLE guide_version_history (
    id              BIGSERIAL PRIMARY KEY,
    guide_id        BIGINT      NOT NULL REFERENCES guide(id),
    version_id      BIGINT      REFERENCES game_version(id),
    content_snapshot JSONB      NOT NULL,
    updated_by      BIGINT      REFERENCES "user"(id),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_gvh_guide ON guide_version_history(guide_id);

-- 3.5 攻略修订记录（作者每次编辑留痕，用于审计）
CREATE TABLE guide_revision (
    id               BIGSERIAL PRIMARY KEY,
    guide_id         BIGINT      NOT NULL REFERENCES guide(id),
    revision_number  INT         NOT NULL,
    changes_summary  TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (guide_id, revision_number)
);

-- 3.6 资讯/专栏
CREATE TABLE article (
    id           BIGSERIAL PRIMARY KEY,
    game_id      BIGINT REFERENCES game(id),
    title        VARCHAR(255)      NOT NULL,
    author_id    BIGINT            NOT NULL REFERENCES "user"(id),
    category     VARCHAR(64),
    content      TEXT,
    published_at TIMESTAMPTZ,
    status       VARCHAR(32)      NOT NULL DEFAULT 'DRAFT',
    created_at   TIMESTAMPTZ      NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ      NOT NULL DEFAULT now(),
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT chk_article_status CHECK (status IN ('DRAFT', 'PENDING_REVIEW', 'PUBLISHED', 'REJECTED', 'ARCHIVED'))
);
CREATE INDEX idx_article_game_status ON article(game_id, status);

-- 3.7 百科条目
CREATE TABLE wiki_entry (
    id           BIGSERIAL PRIMARY KEY,
    game_id      BIGINT      NOT NULL REFERENCES game(id),
    title        VARCHAR(255) NOT NULL,
    content      TEXT,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT now(),
    version_id   BIGINT      REFERENCES game_version(id)
);
CREATE INDEX idx_wiki_game ON wiki_entry(game_id);

-- 3.8 内容来源声明（版权）
CREATE TABLE content_source (
    id           BIGSERIAL PRIMARY KEY,
    guide_id     BIGINT       NOT NULL REFERENCES guide(id),
    source_type  VARCHAR(32)  NOT NULL,        -- BILI_VIDEO / WEB_POST / IMAGE / VIDEO
    source_url   TEXT,
    source_title VARCHAR(255),
    license_note VARCHAR(255),
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX idx_cs_guide ON content_source(guide_id);

-- ============================================================
-- 4. 社区相关
-- ============================================================

-- 4.1 评论
CREATE TABLE comment (
    id         BIGSERIAL PRIMARY KEY,
    target_type VARCHAR(32) NOT NULL,          -- guide / article / wiki / question
    target_id  BIGINT       NOT NULL,
    parent_id  BIGINT       REFERENCES comment(id),
    user_id    BIGINT       NOT NULL REFERENCES "user"(id),
    content    TEXT         NOT NULL,
    like_count BIGINT       NOT NULL DEFAULT 0,
    status     VARCHAR(16)  NOT NULL DEFAULT 'NORMAL',  -- NORMAL / HIDDEN / DELETED
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_comment_target ON comment(target_type, target_id, created_at DESC);

-- 4.2 点赞
CREATE TABLE "like" (
    id          BIGSERIAL PRIMARY KEY,
    target_type VARCHAR(32) NOT NULL,
    target_id   BIGINT      NOT NULL,
    user_id     BIGINT      NOT NULL REFERENCES "user"(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (target_type, target_id, user_id)
);

-- 4.3 收藏
CREATE TABLE favorite (
    id          BIGSERIAL PRIMARY KEY,
    target_type VARCHAR(32) NOT NULL,
    target_id   BIGINT      NOT NULL,
    user_id     BIGINT      NOT NULL REFERENCES "user"(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (target_type, target_id, user_id)
);

-- 4.4 问答
CREATE TABLE question (
    id                 BIGSERIAL PRIMARY KEY,
    game_id            BIGINT      REFERENCES game(id),
    user_id            BIGINT      NOT NULL REFERENCES "user"(id),
    title              VARCHAR(255) NOT NULL,
    description        TEXT,
    bounty_points      INT         NOT NULL DEFAULT 0,
    status             VARCHAR(16) NOT NULL DEFAULT 'OPEN',  -- OPEN / CLOSED / SOLVED
    accepted_answer_id BIGINT,                                -- FK 见 answer 表
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at         TIMESTAMPTZ
);
CREATE INDEX idx_question_game_status ON question(game_id, status);

-- 4.5 回答
CREATE TABLE answer (
    id          BIGSERIAL PRIMARY KEY,
    question_id BIGINT      NOT NULL REFERENCES question(id),
    user_id     BIGINT      NOT NULL REFERENCES "user"(id),
    content     TEXT        NOT NULL,
    like_count  BIGINT      NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);
CREATE INDEX idx_answer_question ON answer(question_id);
ALTER TABLE question ADD CONSTRAINT fk_question_accepted_answer
    FOREIGN KEY (accepted_answer_id) REFERENCES answer(id);

-- 4.6 举报
CREATE TABLE report (
    id          BIGSERIAL PRIMARY KEY,
    reporter_id BIGINT      NOT NULL REFERENCES "user"(id),
    target_type VARCHAR(32) NOT NULL,
    target_id   BIGINT      NOT NULL,
    reason      VARCHAR(255),
    status      VARCHAR(16) NOT NULL DEFAULT 'PENDING',  -- PENDING / PROCESSED / REJECTED
    handled_by  BIGINT      REFERENCES "user"(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_report_status ON report(status);

-- ============================================================
-- 5. AI 与推荐相关
-- ============================================================

-- 5.1 AI 解析任务（source_hash 唯一约束保证幂等）
CREATE TABLE ai_parse_task (
    id              BIGSERIAL PRIMARY KEY,
    source_url      TEXT,
    source_type     VARCHAR(32)      NOT NULL,    -- BILI_VIDEO / WEB_POST / IMAGE
    source_hash     VARCHAR(64)     NOT NULL,    -- SHA-256 十六进制
    status          VARCHAR(32)      NOT NULL DEFAULT 'PENDING',
    result_guide_id BIGINT           REFERENCES guide(id),
    error_msg       TEXT,
    created_at      TIMESTAMPTZ      NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ      NOT NULL DEFAULT now(),
    UNIQUE (source_hash),
    CONSTRAINT chk_ai_task_status CHECK (status IN ('PENDING', 'PROCESSING', 'SUCCEEDED', 'FAILED', 'CANCELLED'))
);
CREATE INDEX idx_ai_task_status ON ai_parse_task(status);

-- 5.2 AI 问答日志
CREATE TABLE ai_qa_log (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT      NOT NULL REFERENCES "user"(id),
    question      TEXT        NOT NULL,
    answer        TEXT,
    source_guides JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_ai_qa_user ON ai_qa_log(user_id);

-- 5.3 用户行为日志（用于推荐）
CREATE TABLE user_behavior_log (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT,                              -- 未登录可为空
    action_type VARCHAR(32) NOT NULL,               -- VIEW / SEARCH / LIKE / FAVORITE / COMMENT
    target_type VARCHAR(32),
    target_id   BIGINT,
    context     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_behavior_user_time ON user_behavior_log(user_id, created_at DESC);
CREATE INDEX idx_behavior_target ON user_behavior_log(target_type, target_id);

-- 5.4 行为批处理任务表（定时聚合进度）
CREATE TABLE behavior_batch (
    id           BIGSERIAL PRIMARY KEY,
    batch_no     VARCHAR(64) NOT NULL UNIQUE,
    status       VARCHAR(16) NOT NULL DEFAULT 'PENDING',  -- PENDING / PROCESSING / DONE / FAILED
    processed_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 6. 工具相关
-- ============================================================

CREATE TABLE interactive_map (
    id            BIGSERIAL PRIMARY KEY,
    game_id       BIGINT      NOT NULL REFERENCES game(id),
    name          VARCHAR(128) NOT NULL,
    map_image_url VARCHAR(500),
    markers       JSONB       NOT NULL DEFAULT '[]',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE build_simulator (
    id         BIGSERIAL PRIMARY KEY,
    game_id    BIGINT       NOT NULL REFERENCES game(id),
    name       VARCHAR(128) NOT NULL,
    config     JSONB        NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE tool_usage_log (
    id         BIGSERIAL PRIMARY KEY,
    tool_type  VARCHAR(32) NOT NULL,   -- MAP / SIMULATOR
    tool_id    BIGINT      NOT NULL,
    user_id    BIGINT      REFERENCES "user"(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_tool_log_tool ON tool_usage_log(tool_type, tool_id);

-- ============================================================
-- 7. 权限、通知与审核
-- ============================================================

-- 7.1 内容审核（机器初判 + 人工复审）
CREATE TABLE content_review (
    id          BIGSERIAL PRIMARY KEY,
    target_type VARCHAR(32)     NOT NULL,
    target_id   BIGINT          NOT NULL,
    reviewer_id BIGINT          REFERENCES "user"(id),
    status      VARCHAR(32)     NOT NULL DEFAULT 'PENDING',
    reason      VARCHAR(255),
    risk_level  VARCHAR(16)     NOT NULL DEFAULT 'LOW',
    reviewed_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT now(),
    CONSTRAINT chk_review_status CHECK (status IN ('PENDING', 'PASSED', 'REJECTED', 'NEED_HUMAN')),
    CONSTRAINT chk_review_risk CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH'))
);
CREATE INDEX idx_review_target ON content_review(target_type, target_id);
CREATE INDEX idx_review_status ON content_review(status);

-- 7.2 审计日志（敏感操作留痕）
CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    operator_id BIGINT REFERENCES "user"(id),
    action      VARCHAR(64) NOT NULL,
    target_type VARCHAR(32),
    target_id   BIGINT,
    before_json JSONB,
    after_json  JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_operator_time ON audit_log(operator_id, created_at DESC);

-- 7.3 通知
CREATE TABLE notification (
    id           BIGSERIAL PRIMARY KEY,
    user_id      BIGINT      NOT NULL REFERENCES "user"(id),
    type         VARCHAR(32) NOT NULL,  -- GUIDE_UPDATE / VERSION_OUTDATED / AI_TASK_DONE / SYSTEM
    title        VARCHAR(255) NOT NULL,
    content      TEXT,
    related_type VARCHAR(32),
    related_id   BIGINT,
    is_read      BOOLEAN     NOT NULL DEFAULT false,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_notification_user_read ON notification(user_id, is_read, created_at DESC);

-- ============================================================
-- 8. 触发器：自动维护 updated_at
-- ============================================================
CREATE TRIGGER trg_user_updated
    BEFORE UPDATE ON "user" FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_game_updated
    BEFORE UPDATE ON game FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_guide_updated
    BEFORE UPDATE ON guide FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_article_updated
    BEFORE UPDATE ON article FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_ai_task_updated
    BEFORE UPDATE ON ai_parse_task FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_map_updated
    BEFORE UPDATE ON interactive_map FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_simulator_updated
    BEFORE UPDATE ON build_simulator FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- user_game_profile 无触发器（仅 updated_at，由应用层维护）

COMMIT;

-- ============================================================
-- 可选：种子数据（游戏分类示例）
-- ============================================================
-- INSERT INTO game (name, category) VALUES ('艾尔登法环', 'RPG'), ('原神', '开放世界');
