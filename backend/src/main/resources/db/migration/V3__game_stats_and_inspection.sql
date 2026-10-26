-- ============================================================
-- V3: 原神与多游戏全维度数值体系、底层机制模型与版本变动巡检审计表
-- ============================================================

BEGIN;

-- 1. 角色全量成长与技能数值表
CREATE TABLE IF NOT EXISTS game_character (
    id                     BIGSERIAL PRIMARY KEY,
    game_id                BIGINT       NOT NULL REFERENCES game(id),
    name                   VARCHAR(128) NOT NULL,
    title                  VARCHAR(128),
    rarity                 INT          NOT NULL DEFAULT 5,
    element                VARCHAR(32)  NOT NULL,
    weapon_type            VARCHAR(32)  NOT NULL,
    region                 VARCHAR(64),
    arkhe                  VARCHAR(32),
    avatar_url             VARCHAR(500),
    splash_url             VARCHAR(500),
    base_stats             JSONB        NOT NULL DEFAULT '[]',   -- 1~90级全14阶段基础生命/攻击白值/防御力
    special_ascension_stat JSONB        NOT NULL DEFAULT '{}',   -- 突破特有属性及各阶段数值
    ascension_materials    JSONB        NOT NULL DEFAULT '[]',   -- 晋阶材料清单
    talents                JSONB        NOT NULL DEFAULT '[]',   -- 普攻/战技/爆发1-10(13)级倍率与机制
    passives               JSONB        NOT NULL DEFAULT '[]',   -- 固有天赋
    constellations         JSONB        NOT NULL DEFAULT '[]',   -- 命之座1-6
    special_mechanics      JSONB        NOT NULL DEFAULT '{}',   -- 附着量/ICD/削韧/生命之契/夜魂/卡肉
    recommendations        JSONB        NOT NULL DEFAULT '{}',   -- 推荐武器/圣遗物/词条
    data_hash              VARCHAR(64)  NOT NULL DEFAULT '',     -- 字段快照哈希(SHA-256)
    version                VARCHAR(32)  NOT NULL DEFAULT '5.0',  -- 生效游戏版本
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (game_id, name)
);
CREATE INDEX IF NOT EXISTS idx_game_char_game_element ON game_character(game_id, element);
CREATE INDEX IF NOT EXISTS idx_game_char_game_rarity  ON game_character(game_id, rarity);

-- 2. 武器数值与精炼成长表
CREATE TABLE IF NOT EXISTS game_weapon (
    id                  BIGSERIAL PRIMARY KEY,
    game_id             BIGINT       NOT NULL REFERENCES game(id),
    name                VARCHAR(128) NOT NULL,
    type                VARCHAR(32)  NOT NULL,
    rarity              INT          NOT NULL DEFAULT 5,
    icon_url            VARCHAR(500),
    base_atk_curve      JSONB        NOT NULL DEFAULT '[]',   -- 1~90级攻击力白值
    sub_stat            JSONB        NOT NULL DEFAULT '{}',   -- 副词条类型与1-90级成长
    refinements         JSONB        NOT NULL DEFAULT '[]',   -- 1-5阶精炼技能与数值
    ascension_materials JSONB        NOT NULL DEFAULT '[]',   -- 突破材料
    data_hash           VARCHAR(64)  NOT NULL DEFAULT '',
    version             VARCHAR(32)  NOT NULL DEFAULT '5.0',
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (game_id, name)
);
CREATE INDEX IF NOT EXISTS idx_game_weapon_game_type ON game_weapon(game_id, type);

-- 3. 圣遗物套装与词条规格表
CREATE TABLE IF NOT EXISTS game_artifact_set (
    id               BIGSERIAL PRIMARY KEY,
    game_id          BIGINT       NOT NULL REFERENCES game(id),
    name             VARCHAR(128) NOT NULL,
    rarity_min       INT          NOT NULL DEFAULT 4,
    rarity_max       INT          NOT NULL DEFAULT 5,
    icon_url         VARCHAR(500),
    two_piece_bonus  TEXT,
    four_piece_bonus TEXT,
    pieces           JSONB        NOT NULL DEFAULT '[]',   -- 生之花/死之羽/时之沙/空之杯/理之冠
    rules_reference  JSONB        NOT NULL DEFAULT '{}',   -- 主词条池与副词条4档强化库
    data_hash        VARCHAR(64)  NOT NULL DEFAULT '',
    version          VARCHAR(32)  NOT NULL DEFAULT '5.0',
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (game_id, name)
);

-- 4. 底层战斗公式与特殊机制规则表
CREATE TABLE IF NOT EXISTS game_mechanic_rule (
    id         BIGSERIAL PRIMARY KEY,
    game_id    BIGINT       NOT NULL REFERENCES game(id),
    category   VARCHAR(64)  NOT NULL,   -- DAMAGE_FORMULA / LEVEL_MULTIPLIER / ICD_SYSTEM / POISE_SYSTEM / REGION_SYSTEM
    title      VARCHAR(128) NOT NULL,
    formula    TEXT,
    parameters JSONB        NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (game_id, category, title)
);
CREATE INDEX IF NOT EXISTS idx_game_mech_game_cat ON game_mechanic_rule(game_id, category);

-- 5. 数值版本巡检变动与审计留痕表
CREATE TABLE IF NOT EXISTS stat_version_audit (
    id              BIGSERIAL PRIMARY KEY,
    game_id         BIGINT       NOT NULL REFERENCES game(id),
    target_type     VARCHAR(32)  NOT NULL,   -- CHARACTER / WEAPON / ARTIFACT / MECHANIC
    target_id       BIGINT,
    target_name     VARCHAR(128) NOT NULL,
    check_batch_no  VARCHAR(64)  NOT NULL,
    status          VARCHAR(32)  NOT NULL DEFAULT 'UNCHANGED', -- UNCHANGED / MODIFIED / NEW_ADDED
    diff_summary    TEXT,
    diff_detail     JSONB        NOT NULL DEFAULT '[]',
    old_hash        VARCHAR(64),
    new_hash        VARCHAR(64),
    checked_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_stat_audit_game_target ON stat_version_audit(game_id, target_type, target_name);
CREATE INDEX IF NOT EXISTS idx_stat_audit_batch       ON stat_version_audit(check_batch_no);
CREATE INDEX IF NOT EXISTS idx_stat_audit_status      ON stat_version_audit(status);

-- 触发器：自动维护 updated_at
DROP TRIGGER IF EXISTS trg_game_character_updated ON game_character;
CREATE TRIGGER trg_game_character_updated
    BEFORE UPDATE ON game_character FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_game_weapon_updated ON game_weapon;
CREATE TRIGGER trg_game_weapon_updated
    BEFORE UPDATE ON game_weapon FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_game_artifact_set_updated ON game_artifact_set;
CREATE TRIGGER trg_game_artifact_set_updated
    BEFORE UPDATE ON game_artifact_set FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_game_mechanic_rule_updated ON game_mechanic_rule;
CREATE TRIGGER trg_game_mechanic_rule_updated
    BEFORE UPDATE ON game_mechanic_rule FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMIT;
