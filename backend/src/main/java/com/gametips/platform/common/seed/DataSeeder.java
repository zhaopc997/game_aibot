package com.gametips.platform.common.seed;

import com.gametips.platform.module.ai.service.AiParseService;
import com.gametips.platform.module.content.domain.Article;
import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.domain.WikiEntry;
import com.gametips.platform.module.content.repository.ArticleRepository;
import com.gametips.platform.module.content.repository.GuideRepository;
import com.gametips.platform.module.content.repository.WikiEntryRepository;
import com.gametips.platform.module.user.domain.Role;
import com.gametips.platform.module.user.domain.User;
import com.gametips.platform.module.user.domain.UserRole;
import com.gametips.platform.module.user.domain.UserStatus;
import com.gametips.platform.module.user.repository.UserRepository;
import com.gametips.platform.module.user.repository.UserRoleRepository;
import com.gametips.platform.module.version.domain.Game;
import com.gametips.platform.module.version.domain.GameVersion;
import com.gametips.platform.module.version.repository.GameRepository;
import com.gametips.platform.module.version.repository.GameVersionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 演示种子数据（原创占位内容，非平台转载）。
 * 由 app.seed.enabled=true 控制，仅在 game 表为空时填充。
 * 内容为通用游戏攻略常识级结构描述，供功能测试使用。
 */
@Slf4j
@Component
@RequiredArgsConstructor
@ConditionalOnProperty(name = "app.seed.enabled", havingValue = "true", matchIfMissing = false)
public class DataSeeder implements CommandLineRunner {

    private final UserRepository userRepository;
    private final UserRoleRepository userRoleRepository;
    private final PasswordEncoder passwordEncoder;
    private final GameRepository gameRepository;
    private final GameVersionRepository gameVersionRepository;
    private final GuideRepository guideRepository;
    private final ArticleRepository articleRepository;
    private final WikiEntryRepository wikiEntryRepository;
    private final AiParseService aiParseService;

    @Override
    @Transactional
    public void run(String... args) {
        seedAccounts();
        if (gameRepository.count() == 0) {
            seedGames();
            log.info("[seed] demo games and guides seeded");
        } else {
            log.info("[seed] game table not empty, skip seeding games");
        }
        seedArticlesAndWiki();
        demoAiPipeline();
        log.info("[seed] demo data verification complete");
    }

    private void seedAccounts() {
        if (!userRepository.existsByUsername("admin")) {
            User admin = new User();
            admin.setUsername("admin");
            admin.setEmail("admin@gametips.local");
            admin.setPasswordHash(passwordEncoder.encode("admin123"));
            admin.setStatus(UserStatus.NORMAL);
            admin.setLevel(10);
            admin.setExp(10000L);
            admin = userRepository.save(admin);
            userRoleRepository.save(new UserRole(admin.getId(), Role.USER));
            userRoleRepository.save(new UserRole(admin.getId(), Role.ADMIN));
        }
        if (!userRepository.existsByUsername("tester")) {
            User tester = new User();
            tester.setUsername("tester");
            tester.setEmail("tester@gametips.local");
            tester.setPasswordHash(passwordEncoder.encode("123456"));
            tester.setStatus(UserStatus.NORMAL);
            tester = userRepository.save(tester);
            userRoleRepository.save(new UserRole(tester.getId(), Role.USER));
        }
    }

    private void seedGames() {
        List<GameSeed> seeds = gameSeeds();
        long authorId = userRepository.findByUsername("tester").orElseThrow().getId();
        for (GameSeed seed : seeds) {
            Game game = new Game();
            game.setName(seed.name());
            game.setCategory(seed.category());
            game.setPlatform(seed.platform());
            game.setDescription(seed.description());
            game.setCurrentVersion(seed.version());
            game = gameRepository.save(game);

            GameVersion gv = new GameVersion();
            gv.setGameId(game.getId());
            gv.setVersionNumber(seed.version());
            gv.setReleaseDate(java.time.LocalDate.now().minusDays(30));
            gv.setPatchNotes(seed.patchNotes());
            gv = gameVersionRepository.save(gv);

            for (GuideSeed g : seed.guides()) {
                Guide guide = new Guide();
                guide.setGameId(game.getId());
                guide.setVersionId(gv.getId());
                guide.setTitle(g.title());
                guide.setAuthorId(authorId);
                guide.setType("MANUAL");
                guide.setDifficulty(g.difficulty());
                guide.setTags(g.tags());
                guide.setSummary(g.summary());
                guide.setContent(buildContent(g.steps()));
                guide.setStatus(GuideStatus.PUBLISHED);
                guide.setLikeCount(g.likeCount());
                guide.setUsefulCount(g.usefulCount());
                guideRepository.save(guide);
            }
            log.info("[seed] game={}, guides={}", seed.name(), seed.guides().size());
        }
    }

    private void demoAiPipeline() {
        try {
            aiParseService.submit("BILI_VIDEO", "https://example.com/video/elden-ring-beginner-guide");
            aiParseService.submit("WEB_POST", "https://example.com/post/genshin-artifact-farming");
            Thread.sleep(1500);
        } catch (Exception e) {
            log.warn("[seed] ai demo skipped: {}", e.getMessage());
        }
    }

    /**
     * 为前几款游戏填充资讯与百科演示数据（仅当 article 表为空时）。
     */
    private void seedArticlesAndWiki() {
        if (articleRepository.count() > 0) {
            return;
        }
        long authorId = userRepository.findByUsername("tester").orElseThrow().getId();
        long now = System.currentTimeMillis();
        var gamed = List.of(
                Map.of("gameId", 1L, "game", "艾尔登法环"),
                Map.of("gameId", 2L, "game", "原神"),
                Map.of("gameId", 3L, "game", "塞尔达传说：王国之泪"),
                Map.of("gameId", 4L, "game", "黑神话：悟空"));
        for (var entry : gamed) {
            Long gameId = (Long) entry.get("gameId");
            String game = (String) entry.get("game");

            Article a = new Article();
            a.setGameId(gameId);
            a.setAuthorId(authorId);
            a.setTitle(game + "版本更新速览:新内容与新玩法解析");
            a.setCategory("版本资讯");
            a.setContent("本文整理了" + game + "近期版本更新的核心内容,包括新玩法、平衡调整与活动预告,帮助玩家快速掌握版本变化。");
            a.setStatus("PUBLISHED");
            a.setPublishedAt(java.time.Instant.ofEpochMilli(now - 86400000L));
            articleRepository.save(a);

            Article a2 = new Article();
            a2.setGameId(gameId);
            a2.setAuthorId(authorId);
            a2.setTitle(game + "社区攻略大赛开启:赢取限定头像框");
            a2.setCategory("活动公告");
            a2.setContent("面向全站玩家的攻略创作大赛现已开启,提交符合要求的攻略即可参与评奖,优秀作品将获得官方推荐与限定奖励。");
            a2.setStatus("PUBLISHED");
            a2.setPublishedAt(java.time.Instant.ofEpochMilli(now - 172800000L));
            articleRepository.save(a2);

            WikiEntry w = new WikiEntry();
            w.setGameId(gameId);
            w.setTitle(game + "入门指南:新手必知基础概念");
            w.setContent("本词条涵盖" + game + "的核心玩法、资源系统与新手常见问题,是快速上手的必备资料。");
            w.setLastUpdated(java.time.Instant.ofEpochMilli(now - 86400000L));
            wikiEntryRepository.save(w);
        }
        log.info("[seed] articles & wiki demo seeded");
    }

    private Map<String, Object> buildContent(List<StepSeed> steps) {
        List<Map<String, Object>> stepList = new ArrayList<>();
        int id = 1;
        for (StepSeed s : steps) {
            Map<String, Object> step = new HashMap<>();
            step.put("step_id", id++);
            step.put("title", s.title());
            step.put("description", s.description());
            step.put("images", List.of());
            step.put("conditions", s.conditions());
            step.put("tools", s.tools());
            stepList.add(step);
        }
        Map<String, Object> content = new HashMap<>();
        content.put("schema_version", "1.0");
        content.put("steps", stepList);
        return content;
    }

    private record StepSeed(String title, String description, List<String> conditions, List<String> tools) {
        StepSeed(String title, String description) {
            this(title, description, List.of(), List.of());
        }
    }

    private record GuideSeed(String title, String difficulty, List<String> tags, String summary,
                             List<StepSeed> steps, long likeCount, long usefulCount) {}

    private record GameSeed(String name, String category, String platform, String description,
                            String version, String patchNotes, List<GuideSeed> guides) {}

    private List<GameSeed> gameSeeds() {
        List<GameSeed> seeds = new ArrayList<>();

        seeds.add(new GameSeed("艾尔登法环", "RPG", "PS5/Xbox/PC", "开放世界魂系动作角色扮演游戏",
                "1.10", "平衡性调整与修正若干 BUG", List.of(
                new GuideSeed("新手开局指南", "EASY", List.of("新手", "开局"), "开局职业选择与初期加点推荐",
                        List.of(
                                new StepSeed("职业选择", "推荐流浪骑士或法师开局，前期生存压力小"),
                                new StepSeed("前期加点", "优先提升生命与耐力，容错更高"),
                                new StepSeed("获取初始武器", "到漂流墓地触发剧情可以获得前期神兵")),
                        320, 280),
                new GuideSeed("全成就速通路线", "HARD", List.of("成就", "速通"), "三周目高效推进成就要点",
                        List.of(
                                new StepSeed("一周目", "走癫火结局路线，收集全部传说武器"),
                                new StepSeed("二周目", "补齐神祇结局相关支线")),
                        96, 74))));

        seeds.add(new GameSeed("原神", "开放世界", "PC/移动/PS", "多国题材开放世界冒险游戏",
                "5.0", "新区域纳塔开放", List.of(
                new GuideSeed("新版本前瞻与抽卡建议", "EASY", List.of("抽卡", "版本"), "围绕当期卡池的抽取优先级与配队建议",
                        List.of(
                                new StepSeed("资源规划", "每周刷完周本与深渊，保留原石给关键命座"),
                                new StepSeed("配队思路", "主C + 副C + 辅助 + 生存位的通用框架")),
                        510, 460),
                new GuideSeed("圣遗物快速毕业", "NORMAL", List.of("圣遗物", "养成"), "刷取路线的效率最大化",
                        List.of(
                                new StepSeed("选择副本", "优先刷词条收益最高的副本"),
                                new StepSeed("强化技巧", "主词条正确即可先用，副词条逐步替换")),
                        402, 388),
                new GuideSeed("深渊平民阵容", "HARD", List.of("深渊", "配队"), "低配阵容通关深渊心得",
                        List.of(
                                new StepSeed("上半区", "聚怪加群伤组合"),
                                new StepSeed("下半区", "对单爆发或护盾组合")),
                        267, 251))));

        seeds.add(new GameSeed("塞尔达传说：王国之泪", "冒险", "Switch", "开放世界动作冒险游戏",
                "1.2.1", "修复低密度雾相关性能问题", List.of(
                new GuideSeed("新手生存技巧", "EASY", List.of("新手", "生存"), "前期获取武器与防寒要点",
                        List.of(
                                new StepSeed("凉爽之地", "初期先在初始空岛上探索完整"),
                                new StepSeed("武器耐久", "善用余料建造大幅提升耐久")),
                        180, 165))));

        seeds.add(new GameSeed("黑神话：悟空", "ARPG", "PC/PS5", "国产神话题材动作游戏",
                "1.0.6", "修复部分 Boss 卡死与闪退问题", List.of(
                new GuideSeed("禁字决配装推荐", "NORMAL", List.of("配装", "Build"), "高输出禁字决流派",
                        List.of(
                                new StepSeed("核心棍式", "重击 + 蓄力为主"),
                                new StepSeed("仙丹分配", "优先攻击与暴击")),
                        233, 210),
                new GuideSeed("全精魄收集清单", "HARD", List.of("收集", "全成就"), "全精魄获取位置整理",
                        List.of(
                                new StepSeed("章节一", "位于火焰山的几处隐藏"),
                                new StepSeed("章节二", "盘丝洞附近的首领掉落")),
                        121, 99))));

        seeds.add(new GameSeed("DOTA 2", "MOBA", "PC", "多人对战竞技游戏",
                "7.38", "全新机制与英雄平衡", List.of(
                new GuideSeed("新手上分英雄推荐", "EASY", List.of("天梯", "新手"), "操作简单、强度稳定的英雄",
                        List.of(
                                new StepSeed("辅助位", "巫妖、拉比克易上手"),
                                new StepSeed("核心位", "幻影长矛手前期强"),
                                new StepSeed("节奏技巧", "15 分钟前抱团推进带节奏")),
                        420, 390),
                new GuideSeed("版本胜率分析", "NORMAL", List.of("版本", "数据"), "当前版本高胜率英雄与打法",
                        List.of(
                                new StepSeed("热门英雄", "针对与克制关系"),
                                new StepSeed("选人策略", "先手后手阵容搭配")),
                        300, 275))));

        seeds.add(new GameSeed("英雄联盟", "MOBA", "PC", "经典 5v5 竞技对战",
                "14.19", "峡谷先锋调整", List.of(
                new GuideSeed("上单对线技巧", "NORMAL", List.of("上单", "对线"), "兵线与换血细节",
                        List.of(
                                new StepSeed("控线", "前三级以小兵仇恨为核心"),
                                new StepSeed("换血", "卡对面补刀瞬间消耗")),
                        350, 310),
                new GuideSeed("打野路线规划", "EASY", List.of("打野", "节奏"), "标准刷野与 Gank 路线",
                        List.of(
                                new StepSeed("首轮刷野", "刷完到三级再考虑抓人"),
                                new StepSeed("资源团", "提前看先锋刷新时间")),
                        260, 240))));

        seeds.add(new GameSeed("CS2", "FPS", "PC", "战术射击游戏",
                "1.37", "武器平衡更新", List.of(
                new GuideSeed("手枪局经济管理", "NORMAL", List.of("经济", "战术"), "手枪局决策与买枪逻辑",
                        List.of(
                                new StepSeed("默认开局", "手枪局存钱起半甲"),
                                new StepSeed("强起时机", "经济差拉大时不再强起")),
                        145, 130))));

        seeds.add(new GameSeed("崩坏：星穹铁道", "RPG", "PC/移动", "回合制科幻 RPG",
                "2.7", "新角色与光锥卡池", List.of(
                new GuideSeed("遗器词条优先级", "EASY", List.of("遗器", "养成"), "输出与辅助角色词条推荐",
                        List.of(
                                new StepSeed("主C", "攻击/暴击/暴伤优先"),
                                new StepSeed("辅助", "速度与效果命中")),
                        410, 375),
                new GuideSeed("深渊满星配队", "HARD", List.of("深渊", "配队"), "当期环境满星阵容",
                        List.of(
                                new StepSeed("队伍一", "虚构稳定解"),
                                new StepSeed("队伍二", "对单攻坚")),
                        198, 170))));

        seeds.add(new GameSeed("明日方舟", "塔防", "PC/移动", "策略塔防游戏",
                "20.9", "新干员登场", List.of(
                new GuideSeed("新人基建布局", "EASY", List.of("基建", "发展"), "宿舍与贸易站的最优编排",
                        List.of(
                                new StepSeed("初期", "宿舍优先提升氛围"),
                                new StepSeed("中后期", "龙门币与经验站平衡")),
                        230, 210))));

        seeds.add(new GameSeed("暗黑破坏神4", "ARPG", "PC/PS/Xbox", "暗黑风格刷宝 ARPG",
                "2.0", "新赛季机制", List.of(
                new GuideSeed("开荒职业推荐", "EASY", List.of("开荒", "职业"), "单赛季开荒强度排行",
                        List.of(
                                new StepSeed("近战", "野蛮人练级快但装备要求高"),
                                new StepSeed("远程", "死灵法师开荒最稳")),
                        190, 180),
                new GuideSeed("终局构筑思路", "HARD", List.of("BD", "终局"), "冲层 BD 的选择与词缀",
                        List.of(
                                new StepSeed("主词缀", "攻速加暴击"),
                                new StepSeed("眷顾点法", "同步升级的三条路线")),
                        88, 76))));

        seeds.add(new GameSeed("博德之门3", "CRPG", "PC/PS5", "回合制 DND 题材 CRPG",
                "7 Hotfix", "修复多任务卡点", List.of(
                new GuideSeed("新手职业推荐", "EASY", List.of("新手", "职业"), "适合第一次接触 DND 的职业",
                        List.of(
                                new StepSeed("坦克", "圣武士开局容错高"),
                                new StepSeed("法术", "法师前期较弱后期强"),
                                new StepSeed("检定技巧", "常用高魅力角色沟通")),
                        260, 240))));

        seeds.add(new GameSeed("赛博朋克2077", "RPG", "PC/PS5/Xbox", "未来都市开放世界 RPG",
                "2.20", "车辆与义体平衡调整", List.of(
                new GuideSeed("黑客流派速成", "EASY", List.of("黑客", "BD"), "前期最强黑客玩法",
                        List.of(
                                new StepSeed("关键芯片", "清道夫路线获取试点重置"),
                                new StepSeed("挥退流", "记忆擦除加时停")),
                        150, 135))));

        seeds.add(new GameSeed("荒野大镖客2", "开放世界", "PC/PS/Xbox", "西部题材开放世界",
                "1.32", "线上模式更新", List.of(
                new GuideSeed("金条快速获取", "NORMAL", List.of("线上", "金条"), "线上模式稳定赚金条途径",
                        List.of(
                                new StepSeed("主线", "主线大动作给大量金条"),
                                new StepSeed("赏金任务", "高星级赏金收益更高")),
                        210, 190))));

        seeds.add(new GameSeed("空洞骑士", "类银河恶魔城", "PC/Switch/PS/Xbox", "2D 类银河战士恶魔城",
                "1.5.8", "最终 DLC 内容上线", List.of(
                new GuideSeed("新手徽章搭配", "EASY", List.of("徽章", "推荐"), "前期实用徽章组合",
                        List.of(
                                new StepSeed("生存", "迅捷劈砍加虫歌"),
                                new StepSeed("探索", "地图师加指南针"),
                                new StepSeed("Boss", "力量加快速聚集")),
                        245, 230))));

        seeds.add(new GameSeed("以撒的结合：忏悔", "Rougelike", "PC", "Roguelike 随机地牢",
                "Repentance+", "新内容扩充", List.of(
                new GuideSeed("全成就解锁路线", "HARD", List.of("成就", "全收集"), "从普通结局到标记的路线",
                        List.of(
                                new StepSeed("基础结局", "击败母亲线"),
                                new StepSeed("腹死胎中", "解锁神性干预")),
                        90, 82))));

        seeds.add(new GameSeed("Apex 英雄", "FPS", "PC/PS/Xbox", "战术竞技大逃杀",
                "S23", "新赛季英雄改动", List.of(
                new GuideSeed("传奇搭配与战术", "NORMAL", List.of("战术", "传奇"), "三人小队标准阵容",
                        List.of(
                                new StepSeed("侦查", "探路者负责信息"),
                                new StepSeed("布雷", "瓦尔基里开团"),
                                new StepSeed("合计", "队伍分工明确后推进")),
                        175, 160))));

        seeds.add(new GameSeed("Valorant", "FPS", "PC", "5v5 战术射击",
                "9.0", "新特工英雄上线", List.of(
                new GuideSeed("瞄准训练方法", "NORMAL", List.of("训练", "枪法"), "每日练枪模板",
                        List.of(
                                new StepSeed("热手", "死斗模式 200 击杀"),
                                new StepSeed("爆头线", "练习场拉枪")),
                        160, 150))));

        seeds.add(new GameSeed("炉石传说", "卡牌", "PC/移动", "策略卡牌对战",
                "30.4", "新扩展版本", List.of(
                new GuideSeed("快攻卡组效率上分", "EASY", List.of("天梯", "卡组"), "当前版本上分最快的快攻卡组",
                        List.of(
                                new StepSeed("构筑", "低费曲线加铺场"),
                                new StepSeed("节奏", "前四回合决定胜负")),
                        300, 270))));

        seeds.add(new GameSeed("云顶之弈", "自走棋", "PC/移动", "英雄联盟自走棋模式",
                "13.90", "海克斯与羁绊调整", List.of(
                new GuideSeed("当前版本上分阵容", "EASY", List.of("阵容", "上分"), "版本强势阵容推荐",
                        List.of(
                                new StepSeed("前期", "保连胜速冲人口"),
                                new StepSeed("成型阵容", "法师体系主C"),
                                new StepSeed("运营", "留关键打工牌")),
                        420, 390))));

        seeds.add(new GameSeed("永劫无间", "动作", "PC/主机", "武侠题材多人竞技",
                "3.8", "新地图与新武器", List.of(
                new GuideSeed("新手连段教学", "NORMAL", List.of("连段", "教学"), "基础连招与冻结技巧",
                        List.of(
                                new StepSeed("基础", "普攻接裂空"),
                                new StepSeed("进阶", "剑气接蓄力")),
                        130, 115))));

        seeds.add(new GameSeed("幻塔", "开放世界", "PC/移动", "二次元开放世界 MMORPG",
                "4.0", "新地图开放", List.of(
                new GuideSeed("新人资源规划", "EASY", List.of("养成", "资源"), "开局资源分配建议",
                        List.of(
                                new StepSeed("氪金", "月卡性价比最高"),
                                new StepSeed("体力", "优先刷材料本")),
                        140, 125))));

        seeds.add(new GameSeed("Phasmophobia", "恐怖", "PC/主机", "多人合作的鬼屋调查游戏",
                "0.10", "新鬼种与道具", List.of(
                new GuideSeed("识别鬼种流程图", "NORMAL", List.of("攻略", "鉴别"), "通过证据快速判断鬼种",
                        List.of(
                                new StepSeed("第一步", "温度计确认冷点"),
                                new StepSeed("第二步", "紫外线与眼珠证据"),
                                new StepSeed("第三步", "综合三证据锁定")),
                        95, 90))));

        return seeds;
    }
}