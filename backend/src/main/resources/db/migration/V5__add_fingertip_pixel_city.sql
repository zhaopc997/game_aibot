-- ============================================================
-- V5: 新增热门手游《指尖像素城》(Game 32) 游戏元数据、官方攻略与图鉴知识库
-- ============================================================

BEGIN;

-- 1. 注册游戏 32: 指尖像素城
INSERT INTO game (id, name, alias, platform, category, cover_url, description, current_version, created_at, updated_at)
VALUES (
    32,
    '指尖像素城',
    'Pixel City/指尖像素/像素城',
    '移动端 (微信小游戏/iOS/Android)',
    '放置卡牌RPG',
    '/games/pixel_city/cover.svg',
    '超人气像素风策略放置卡牌手游。以神话与虚空异界为背景，融合阵奕布阵、怒气循环博弈、破盾斩杀与专属圣物体系。玩家可自由搭配青龙、辉夜姬、雅典娜等数十位SP神将，越战挑战通天塔、阵奕虚空与跨服竞技巅峰赛！',
    'V2.4.0 虚空降临',
    NOW(), NOW()
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    alias = EXCLUDED.alias,
    platform = EXCLUDED.platform,
    category = EXCLUDED.category,
    cover_url = EXCLUDED.cover_url,
    description = EXCLUDED.description,
    current_version = EXCLUDED.current_version,
    updated_at = NOW();

-- 确保自增序列不落后
SELECT setval('game_id_seq', GREATEST((SELECT MAX(id) FROM game), 32));

-- 2. 插入精选攻略 (关联 admin 账号)
DO $$
DECLARE
    v_author_id BIGINT;
BEGIN
    SELECT id INTO v_author_id FROM "user" WHERE username IN ('admin', 'tester') ORDER BY id ASC LIMIT 1;
    IF v_author_id IS NOT NULL THEN
        -- 攻略 1: 新手开荒与平民运营
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, created_at, updated_at)
        VALUES (
            32,
            '《指尖像素城》新手开荒与70亿战力平民运营全指南',
            v_author_id,
            'MANUAL',
            'EASY',
            '["新手", "平民运营", "达标礼", "阵奕虚空"]'::jsonb,
            '详解开局资源规划、招募达标活动轮转策略、平民0痕战神培养路线与高性价比战力飙升法则。',
            '{
                "schema_version": "1.0",
                "steps": [
                    {
                        "step_id": 1,
                        "title": "资源积累：非达标周绝不乱抽招募卷",
                        "description": "游戏内招募活动按周轮换达标礼，积攒至少800抽招募卷在虚空招募周集中释放，拿满核心SP神将碎片与专属圣物宝箱。",
                        "images": [],
                        "conditions": ["保存星钻与招募卷"],
                        "tools": ["达标礼活动面板"]
                    },
                    {
                        "step_id": 2,
                        "title": "阵营过渡：平民首选自然+水系平滑推图",
                        "description": "前期优先培养伊格拉（自然奶妈）+ 洛神（净化）+ 泰坦（反震巨坦），依靠伊格拉超量治疗转化增伤机制快速越战破关。",
                        "images": [],
                        "conditions": ["通天塔1~200层"],
                        "tools": ["冒险通天塔"]
                    },
                    {
                        "step_id": 3,
                        "title": "圣物锁定：首选终焉之眼与永恒圣杯",
                        "description": "圣物许愿池优先选择终焉之眼（青龙毕业）与永恒圣杯（全员开局怒气与护盾），形成第一套完整的怒气爆发链。",
                        "images": [],
                        "conditions": ["圣物寻宝池解锁"],
                        "tools": ["圣物锻造台"]
                    }
                ]
            }'::jsonb,
            'PUBLISHED',
            328,
            289,
            NOW(),
            NOW()
        );

        -- 攻略 2: T0减怒队与火克冰阵容深度实战
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, created_at, updated_at)
        VALUES (
            32,
            '巅峰竞技场T0阵容深度解析：辉夜雪女减怒队 vs 沃尔卡凤凰灼烧队',
            v_author_id,
            'MANUAL',
            'HARD',
            '["PVP", "阵容搭配", "减怒队", "火克冰"]'::jsonb,
            '顶端局50亿战力跨战力博弈核心：减怒压制流与灼烧引爆真伤流的排兵布阵与圣物符文定制。',
            '{
                "schema_version": "1.0",
                "steps": [
                    {
                        "step_id": 1,
                        "title": "控怒核心机制：辉夜姬 + 雪女双封锁",
                        "description": "辉夜姬受击偷怒并施放全屏禁怒，配合雪女全屏冰冻减35怒，使敌方高爆发主C全程释放不出怒气大招，彻底沦为白板。",
                        "images": [],
                        "conditions": ["辉夜姬+雪女在阵"],
                        "tools": ["竞技场巅峰挑战"]
                    },
                    {
                        "step_id": 2,
                        "title": "火克冰奇袭：沃尔卡 + 凤凰火系狂暴队",
                        "description": "当遭遇极致冰雪减怒防守队时，换上沃尔卡与凤凰。火属性天生对冰系增伤100%且免冰冻，配合凤凰全员免死轻松跨战力反杀！",
                        "images": [],
                        "conditions": ["针对冰雪阵容"],
                        "tools": ["阵型变换"]
                    }
                ]
            }'::jsonb,
            'PUBLISHED',
            412,
            380,
            NOW(),
            NOW()
        );

        -- 3. 插入资讯
        INSERT INTO article (game_id, title, author_id, category, content, published_at, status, created_at, updated_at)
        VALUES (
            32,
            '《指尖像素城》V2.4.0 虚空降临版本更新公告：SP雅典娜携破盾长矛破晓登场！',
            v_author_id,
            '版本资讯',
            '亲爱的城主大人：本次 V2.4.0 版本正式迎来虚空战神【雅典娜】焕新降临！其特化破盾长矛对屏障护盾造成300%破坏伤害，彻底重构护盾对抗生态！同步开启秋行枫林庆典与阵奕虚空全新高难秘境。',
            NOW(),
            'PUBLISHED',
            NOW(),
            NOW()
        );

        -- 4. 插入百科入门
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (
            32,
            '《指尖像素城》核心战斗属性与阵奕克制词条百科',
            '指尖像素城包含雷、火、冰、流水、疾风、大地、光辉、暗夜、百妖与虚空十大系别。怒气上限统一为100点，普攻回怒25点，受击回怒10点。阵奕系统通过同阵营共鸣激发全队攻防血量百分比光环，助战位角色可在特定回合无伤施放全队增益。',
            NOW()
        );
    END IF;
END $$;

COMMIT;
