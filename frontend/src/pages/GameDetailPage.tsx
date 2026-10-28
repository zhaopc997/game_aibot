import { Link, useParams } from 'react-router-dom'
import { Heart, Map as MapIcon, Calculator, Sparkles, ChevronLeft, MessageSquare, BookOpen, Newspaper, FileText, Users, Swords, Gem, Flame } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { Tag } from '@/components/ui/Tag'
import { Button } from '@/components/ui/Button'
import { HoverCard } from '@/components/ui/Card'
import { GameCover } from '@/components/GameCover'
import client, { unwrap } from '@/api/client'
import {
  CharacterStatsTab,
  WeaponStatsTab,
  ArtifactStatsTab,
  MechanicRulesTab,
  CharacterData,
  WeaponData,
  ArtifactData,
  MechanicRuleData,
} from '@/components/stats/GameStatsViews'

interface Game {
  /** 英文名/别名（部分游戏用于匹配展示逻辑） */
  alias?: string | null
  id: number
  name: string
  category?: string
  platform?: string
  description?: string
  currentVersion?: string
  coverUrl?: string | null
}

interface Guide {
  id: number
  title: string
  summary?: string
  tags: string[]
  difficulty?: string
  likeCount: number
  usefulCount: number
  updatedAt: string
}

interface Article {
  id: number
  title: string
  category?: string
  content?: string
  publishedAt?: string
}

interface WikiEntry {
  id: number
  title: string
  content?: string
}

interface Question {
  id: number
  title: string
  description?: string
  status: string
  createdAt: string
}

interface PageResult<T> { items: T[]; nextCursor?: string | null }

type TabKey = 'guides' | 'characters' | 'weapons' | 'artifacts' | 'mechanics' | 'news' | 'wiki' | 'qa'

export default function GameDetailPage() {
  const { id } = useParams()
  const tabsRef = useRef<HTMLDivElement>(null)
  const [game, setGame] = useState<Game | null>(null)
  const [guides, setGuides] = useState<Guide[]>([])
  const [articles, setArticles] = useState<Article[]>([])
  const [wiki, setWiki] = useState<WikiEntry[]>([])
  const [questions, setQuestions] = useState<Question[]>([])
  const [characters, setCharacters] = useState<CharacterData[]>([])
  const [weapons, setWeapons] = useState<WeaponData[]>([])
  const [artifacts, setArtifacts] = useState<ArtifactData[]>([])
  const [mechanics, setMechanics] = useState<MechanicRuleData[]>([])
  const [tab, setTab] = useState<TabKey>('guides')
  const [loading, setLoading] = useState(true)

  const scrollToTab = (targetTab: TabKey) => {
    setTab(targetTab)
    setTimeout(() => {
      tabsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 50)
  }

const FALLBACK_GAMES_MAP: Record<number, Partial<Game>> = {
  1: { id: 1, name: '艾尔登法环', category: 'RPG', platform: 'PS5/Xbox/PC', currentVersion: '1.14', description: 'FromSoftware 开发的大型开放世界黑暗奇幻动作 RPG，由宫崎英高与乔治·R·R·马丁联袂构建交界地神话。' },
  2: { id: 2, name: '原神', category: '开放世界', platform: 'PC/移动/PS5', currentVersion: '5.0', description: '米哈游自主研发的开放世界冒险 RPG，玩家将扮演旅行者，在七元素交汇的提瓦特大陆展开自由冒险。' },
  3: { id: 3, name: '塞尔达传说：王国之泪', category: '冒险', platform: 'Switch', currentVersion: '1.2.1', description: '任天堂出品的开放世界动作冒险巨作，引入究极手、余料建造等颠覆性创意，畅游海拉鲁天空、陆地与地底。' },
  4: { id: 4, name: '黑神话：悟空', category: 'ARPG', platform: 'PC/PS5', currentVersion: '1.0.9', description: '游戏科学开发的中国神话题材顶级单机动作 RPG，以西游记为底色，重走重山万水，再现神佛妖魔交织的东方史诗。' },
  5: { id: 5, name: 'DOTA 2', category: 'MOBA', platform: 'PC', currentVersion: '7.37d', coverUrl: null, description: 'V社全球顶级多人战术竞技游戏，深度正反补、高低地视野与百名英雄博弈。' },
  6: { id: 6, name: '英雄联盟', category: 'MOBA', platform: 'PC', currentVersion: '14.19', description: '拳头游戏开发、腾讯代理的全球风靡多人对战竞技网游，拥有召唤师峡谷、云顶之弈等多重竞技模式与深厚宇宙背景。' },
  7: { id: 7, name: 'CS2', category: 'FPS', platform: 'PC', currentVersion: '1.39', description: 'V社全球顶级战术第一人称射击游戏，起源2引擎动态体积烟雾与亚毫秒级 Sub-tick 物理判定。' },
  8: { id: 8, name: '崩坏：星穹铁道', category: 'RPG', platform: 'PC/移动/PS5', currentVersion: '2.7', description: '米哈游银河冒险策略银河 RPG，乘坐星穹列车穿行诸界，探索开拓命途，体验电影级回合制策略战斗。' },
  9: { id: 9, name: '明日方舟', category: '塔防', platform: '移动端', currentVersion: '2.3.0', coverUrl: null, description: '鹰角网络策略自走与战术塔防 RPG，指挥罗德岛各职阶干员应对源石灾难与矿石病危机。' },
  10: { id: 10, name: '暗黑破坏神4', category: 'ARPG', platform: 'PC/PS/Xbox', currentVersion: '2.0.4', coverUrl: null, description: '暴雪出品的暗黑奇幻动作刷宝 RPG，六大职业构筑、暗金神话与深坑冲层。' },
  11: { id: 11, name: '博德之门3', category: 'CRPG', platform: 'PC/PS5/Xbox', currentVersion: 'Patch 7', coverUrl: null, description: '拉瑞安工作室开发的 TGA 年度最佳神作，D&D 5e 规则、起源同伴深度叙事与无限可能。' },
  12: { id: 12, name: '赛博朋克2077', category: 'RPG', platform: 'PC/PS5/Xbox', currentVersion: '2.2', coverUrl: null, description: 'CDPR 开发的开放世界动作冒险巨作，穿行夜之城，义体过载与斯安威逊时停刀剑战斗。' },
  13: { id: 13, name: '荒野大镖客2', category: '开放世界', platform: 'PC/PS/Xbox', currentVersion: '1.32', coverUrl: null, description: 'Rockstar 巅峰级西部开放世界史诗巨作，亚瑟·摩根的救赎绝唱，拟真生态与死神之眼极速拔枪。' },
  14: { id: 14, name: '空洞骑士', category: '类银河恶魔城', platform: 'PC/Switch/PS/Xbox', currentVersion: '1.5.78', coverUrl: null, description: 'Team Cherry 现象级类银河恶魔城手绘神作，探索衰落的庞大地下虫之王国，骨钉剑技与深渊暗影法术。' },
  15: { id: 15, name: '以撒的结合：忏悔', category: 'Rougelike', platform: 'PC/主机', currentVersion: 'Repentance+', coverUrl: null, description: '肉鸽地牢射击开拓级神作，千百种道具异能组合与变身，命运六面骰与硫磺火血泪清洗地牢。' },
  16: { id: 16, name: 'Apex 英雄', category: 'FPS', platform: 'PC/PS/Xbox', currentVersion: 'Season 23', coverUrl: null, description: '重生娱乐出品的快节奏战术战术竞技射击游戏，传奇技能、滑铲跳身法与枪法协同。' },
  17: { id: 17, name: 'Valorant', category: 'FPS', platform: 'PC', currentVersion: '9.06', coverUrl: null, description: '拳头游戏 5v5 战术射击竞技力作，特工技能配合急停枪法，爆头一枪毙命与精密经济博弈。' },
  18: { id: 18, name: '炉石传说', category: '卡牌', platform: 'PC/移动', currentVersion: '30.4', coverUrl: null, description: '暴雪出品的全球风靡集换式卡牌对战游戏，魔兽英雄齐聚旅店，精妙水晶曲线、战吼亡语与宇宙套牌。' },
  19: { id: 19, name: '云顶之弈', category: '自走棋', platform: 'PC/移动', currentVersion: 'Set 12', coverUrl: null, description: '英雄联盟经典自走棋模式，弈子升星、羁绊组建、海克斯科技与装备合成。' },
  20: { id: 20, name: '永劫无间', category: '动作', platform: 'PC/主机/移动', currentVersion: 'Season 14', coverUrl: null, description: '网易 24 Entertainment 国风武侠动作吃鸡，冷热兵器博弈、飞索走位与剪刀石头布振刀机制。' },
  21: { id: 21, name: '幻塔', category: '开放世界', platform: 'PC/移动/主机', currentVersion: '3.8', description: '完美世界自主研发的轻科幻开放世界手游，拟态角色、武器充能与幻想时间时停机制。' },
  22: { id: 22, name: 'Phasmophobia', category: '恐怖调查', platform: 'PC/VR/主机', currentVersion: 'v0.10', description: 'Kinetic Games 开发的 4 人联机心理恐怖调查神作，利用 EMF、通灵盒等探测设备识别幽灵种类并存活撤离。' },
  23: { id: 23, name: '火线战姬', category: '机甲射击', platform: 'PC/移动', currentVersion: 'v1.2', description: '未来赛博科幻二次元动作射击游戏，操作搭载高科技机甲的战姬少女，在近未来废墟都市抵御机械异变浪潮。' },
  24: { id: 24, name: '王者荣耀', category: 'MOBA', platform: '移动端 (iOS/Android)', currentVersion: 'S36', coverUrl: null, description: '腾讯天美工作室群研发的国民级 5v5 团队公平竞技手游，丰富英雄生态与局内出装铭文体系。' },
  25: { id: 25, name: '绝区零', category: 'ARPG', platform: 'PC/移动/PS5', currentVersion: '1.2', coverUrl: null, description: '米哈游全新 3D 动作游戏，潮酷现代都市、极爽击破失衡连携与混沌异常机制。' },
  26: { id: 26, name: '鸣潮', category: '开放世界', platform: 'PC/iOS/Android', currentVersion: '1.3', coverUrl: null, description: '库洛游戏自研开放世界动作大作，滑翔飞檐走壁、协奏变奏连携、极限闪避与爽快弹刀博弈。' },
  27: { id: 27, name: '和平精英', category: '战术竞技', platform: '移动端 (iOS/Android)', currentVersion: '1.27', coverUrl: null, description: '腾讯光子工作室群自研打造的国民级战术竞技射击手游，百人同场竞技与真实弹道射击。' },
  28: { id: 28, name: '金铲铲之战', category: '策略自走棋', platform: '移动端 (iOS/Android)', currentVersion: 'S12', coverUrl: null, description: '腾讯官方授权的正版自走棋手游，八人同台博弈、融合英雄提升战力与海克斯强化。' },
  29: { id: 29, name: '阴阳师', category: '和风RPG', platform: '移动端 (iOS/Android/PC)', currentVersion: 'v1.7', coverUrl: null, description: '网易游戏自研的和风回合制 RPG 手游，人鬼共生的平安时代，式神收集与深度御魂养成。' },
  30: { id: 30, name: '崩坏3', category: '3D动作', platform: 'PC/移动端', currentVersion: 'v7.8', coverUrl: null, description: '米哈游自主研发的 3D 全视角动作手游，点燃国创动作游戏之魂，时空断裂与主机级打击感。' },
  31: { id: 31, name: '重返未来：1999', category: '复古神秘学RPG', platform: 'PC/移动端', currentVersion: 'v2.2', coverUrl: null, description: '深蓝互动研发的复古神秘学策略 RPG 手游，穿梭于暴雨引发的时代倒退之中，探寻历史真相。' },
  32: { id: 32, name: '指尖像素城', category: '放置卡牌RPG', platform: '移动端 (微信小游戏/iOS/Android)', currentVersion: 'V2.4.0', coverUrl: '/games/pixel_city/cover.svg', description: '超人气像素风策略放置卡牌手游，神明与虚空神将、阵奕布阵、怒气压制与专属圣物。' },
}

  useEffect(() => {
    if (!id) return
    setLoading(true)
    const gid = Number(id)
    Promise.all([
      client.get(`/games/${gid}`).catch(() => null),
      client.get(`/guides?gameId=${gid}&status=PUBLISHED&size=50`).catch(() => null),
      client.get(`/articles?gameId=${gid}`).catch(() => null),
      client.get(`/wiki/${gid}`).catch(() => null),
      client.get(`/questions?gameId=${gid}`).catch(() => null),
      client.get(`/games/${gid}/characters?size=300`).catch(() => null),
      client.get(`/games/${gid}/weapons?size=400`).catch(() => null),
      client.get(`/games/${gid}/artifacts?size=100`).catch(() => null),
      client.get(`/games/${gid}/mechanics`).catch(() => null),
    ]).then(([g, gl, al, wl, ql, cl, wpl, arl, mel]) => {
      let resolvedGame: Game | null = null
      if (g) {
        try { resolvedGame = unwrap<Game>(g) } catch {}
      }
      if (!resolvedGame && FALLBACK_GAMES_MAP[gid]) {
        resolvedGame = FALLBACK_GAMES_MAP[gid] as Game
      }
      if (resolvedGame) setGame(resolvedGame)

      const guidesList = gl ? (unwrap<PageResult<Guide>>(gl).items || []) : []
      const charactersList = cl ? (unwrap<PageResult<CharacterData>>(cl).items || []) : []
      const weaponsList = wpl ? (unwrap<PageResult<WeaponData>>(wpl).items || []) : []
      const artifactsList = arl ? (unwrap<PageResult<ArtifactData>>(arl).items || []) : []
      const mechanicsList = mel ? (unwrap<MechanicRuleData[]>(mel) || []) : []
      const articlesList = al ? (unwrap<Article[]>(al) || []) : []
      const wikiList = wl ? (unwrap<WikiEntry[]>(wl) || []) : []
      const questionsList = ql ? (unwrap<Question[]>(ql) || []) : []

      setGuides(guidesList)
      setArticles(articlesList)
      setWiki(wikiList)
      setQuestions(questionsList)
      setCharacters(charactersList)
      setWeapons(weaponsList)
      setArtifacts(artifactsList)
      setMechanics(mechanicsList)

      // 如果攻略为空，优先展示有实质数值数据的标签页
      if (guidesList.length === 0) {
        if (charactersList.length > 0) {
          setTab('characters')
        } else if (weaponsList.length > 0) {
          setTab('weapons')
        } else if (artifactsList.length > 0) {
          setTab('artifacts')
        } else if (mechanicsList.length > 0) {
          setTab('mechanics')
        } else if (wikiList.length > 0) {
          setTab('wiki')
        } else if (articlesList.length > 0) {
          setTab('news')
        }
      }
    }).finally(() => setLoading(false))
  }, [id])

  if (loading && !game) return <div className="pt-20 text-center text-ink-500">加载中…</div>
  if (!game) return <div className="pt-20 text-center text-ink-500">游戏不存在</div>

  const isLol = Boolean(game.name?.includes('英雄联盟') || game.id === 6)
  const isHok = Boolean(game.name?.includes('王者荣耀') || game.id === 24)
  const isArknights = Boolean(game.name?.includes('明日方舟') || game.id === 9)
  const isZzz = Boolean(game.name?.includes('绝区零') || game.id === 25)
  const isMoba = isLol || isHok || Boolean(game.category?.includes('MOBA'))
  const isHsr = Boolean(game.name?.includes('星穹铁道') || game.id === 8)
  const isWukong = Boolean(game.name?.includes('悟空') || game.name?.includes('黑神话') || game.id === 4)
  const isEldenRing = Boolean(game.name?.includes('艾尔登法环') || game.alias?.includes('Elden Ring') || game.id === 1)
  const isZelda = Boolean(game.name?.includes('塞尔达') || game.name?.includes('王国之泪') || game.id === 3)

  const isHonkai3 = Boolean(game.name?.includes('崩坏3') || game.id === 30)
  const isTft = Boolean(game.name?.includes('金铲铲') || game.name?.includes('云顶') || game.id === 28 || game.id === 19)
  const isNaraka = Boolean(game.name?.includes('永劫无间') || game.id === 20)

  const characterTabLabel = isHonkai3 ? '女武神装甲' : isTft ? '弈子图鉴' : isNaraka ? '英雄豪杰' : isArknights ? '干员图鉴' : isZzz ? '代理人图鉴' : (isHok || isMoba) ? '英雄图鉴' : isWukong ? '天命流派' : isEldenRing ? '流派构筑' : isZelda ? '林克能力' : '角色图鉴'
  const weaponTabLabel = isHonkai3 ? '超限神兵' : isTft ? '装备合成' : isNaraka ? '神兵武备' : isHok ? '局内装备' : isArknights ? '专属模组' : isZzz ? '音擎图鉴' : isMoba ? '装备图鉴' : isHsr ? '光锥图鉴' : isWukong ? '兵刃图鉴' : isEldenRing ? '神兵触媒' : isZelda ? '神兵余料' : '武器装备'
  const artifactTabLabel = isHonkai3 ? '圣痕体系' : isTft ? '羁绊与符文' : isNaraka ? '专属魂玉' : isHok ? '铭文体系' : isArknights ? '职业分支' : isZzz ? '驱动盘' : isMoba ? '符文体系' : isHsr ? '遗器体系' : isWukong ? '披挂防具' : isEldenRing ? '传奇护符' : isZelda ? '防具套装' : '圣遗物'
  const mechanicTabLabel = isHonkai3 ? '星环与机制' : isTft ? '核心对局机制' : isNaraka ? '拼刀与振刀法则' : isHok ? '对战机制' : isArknights ? '作战机制' : isZzz ? '动作机制' : isMoba ? '机制法则' : isWukong ? '战斗法则' : isEldenRing ? '交界地法则' : isZelda ? '物理法则' : '战斗机制'

  const tabs: { key: TabKey; label: string; icon: React.ReactNode; count: number }[] = [
    { key: 'guides', label: '攻略', icon: <FileText size={15} />, count: guides.length },
    ...(characters.length > 0 ? [{ key: 'characters' as TabKey, label: characterTabLabel, icon: <Users size={15} />, count: characters.length }] : []),
    ...(weapons.length > 0 ? [{ key: 'weapons' as TabKey, label: weaponTabLabel, icon: <Swords size={15} />, count: weapons.length }] : []),
    ...(artifacts.length > 0 ? [{ key: 'artifacts' as TabKey, label: artifactTabLabel, icon: <Gem size={15} />, count: artifacts.length }] : []),
    ...(mechanics.length > 0 ? [{ key: 'mechanics' as TabKey, label: mechanicTabLabel, icon: <Flame size={15} />, count: mechanics.length }] : []),
    { key: 'news', label: '资讯', icon: <Newspaper size={15} />, count: articles.length },
    { key: 'wiki', label: '百科', icon: <BookOpen size={15} />, count: wiki.length },
    { key: 'qa', label: '讨论', icon: <MessageSquare size={15} />, count: questions.length },
  ]

  return (
    <div className="pt-8 pb-20 space-y-10">
      <Link to="/games" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700">
        <ChevronLeft size={14} /> 返回游戏库
      </Link>

      {/* Hero */}
      <section className="rounded-4xl bg-gradient-to-br from-accent-50 to-canvas border border-ink-100/40 p-8 md:p-12 relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 h-60 w-60 rounded-full bg-accent-200/40 blur-3xl" />
        <div className="relative grid md:grid-cols-[auto_1fr] gap-8 items-center">
          <div className="h-40 w-40 md:h-48 md:w-48 rounded-3xl bg-surface shadow-soft overflow-hidden border border-ink-100/40 relative">
            <GameCover
              src={game.coverUrl}
              gameId={game.id}
              alt={game.name}
              className="h-full w-full"
              emojiClassName="h-full w-full grid place-items-center text-7xl select-none"
            />
          </div>
          <div>
            <h1 className="text-3xl md:text-4xl font-display font-semibold text-ink-900">
              {game.name}
              {game.currentVersion && (
                <span className="ml-3 text-base font-sans font-normal text-ink-500">v{game.currentVersion}</span>
              )}
            </h1>
            <div className="mt-3 flex items-center gap-2 flex-wrap">
              {game.category && <Tag>{game.category}</Tag>}
              {game.platform && game.platform.split('/').map((p) => <Tag key={p} variant="outline">{p.trim()}</Tag>)}
            </div>
            {game.description && <p className="mt-4 text-ink-700 max-w-2xl">{game.description}</p>}
            <div className="mt-6 flex items-center gap-2 flex-wrap">
              {characters.length > 0 && (
                <Button variant="outline" onClick={() => scrollToTab('characters')} className="border-accent-200 text-accent-700 hover:bg-accent-50">
                  <Users size={16} className="text-accent-500" /> {characterTabLabel} ({characters.length})
                </Button>
              )}
              {weapons.length > 0 && (
                <Button variant="outline" onClick={() => scrollToTab('weapons')} className="border-accent-200 text-accent-700 hover:bg-accent-50">
                  <Swords size={16} className="text-accent-500" /> {weaponTabLabel} ({weapons.length})
                </Button>
              )}
              {artifacts.length > 0 && (
                <Button variant="outline" onClick={() => scrollToTab('artifacts')} className="border-accent-200 text-accent-700 hover:bg-accent-50">
                  <Gem size={16} className="text-accent-500" /> {artifactTabLabel} ({artifacts.length})
                </Button>
              )}
              {mechanics.length > 0 && (
                <Button variant="outline" onClick={() => scrollToTab('mechanics')}>
                  <Flame size={16} className="text-accent-500" /> {mechanicTabLabel} ({mechanics.length})
                </Button>
              )}
              <Link to={`/games/${id}/maps`}>
                <Button variant="outline"><MapIcon size={16} /> 互动地图</Button>
              </Link>
              <Link to={`/games/${id}/simulators`}>
                <Button variant="outline"><Calculator size={16} /> 模拟器</Button>
              </Link>
              <Link to="/ai">
                <Button variant="soft"><Sparkles size={16} /> AI 帮帮我</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Tabs */}
      <section ref={tabsRef}>
        <div className="flex items-center gap-1 border-b border-ink-100 mb-6 overflow-x-auto">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`inline-flex items-center gap-1.5 px-4 h-11 text-sm font-medium border-b-2 transition-colors shrink-0 ${
                tab === t.key
                  ? 'border-accent-500 text-accent-700'
                  : 'border-transparent text-ink-500 hover:text-ink-700'
              }`}
            >
              {t.icon} {t.label}
              <span className="text-xs text-ink-400">({t.count})</span>
            </button>
          ))}
        </div>

        <div className="space-y-3">
          {tab === 'guides' && (
            guides.length === 0 ? <Empty text="暂无攻略" /> : guides.map((g) => (
              <Link key={g.id} to={`/guides/${g.id}`}>
                <HoverCard className="flex items-center gap-4 p-4">
                  <div className="h-16 w-20 rounded-2xl bg-gradient-to-br from-accent-100 to-canvas grid place-items-center text-3xl shrink-0">📖</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      {g.tags?.slice(0, 2).map((t) => <Tag key={t} size="sm">{t}</Tag>)}
                      {g.difficulty && <span className="text-xs text-ink-500">{g.difficulty}</span>}
                    </div>
                    <h3 className="text-base font-medium text-ink-900 truncate">{g.title}</h3>
                    {g.summary && <p className="text-sm text-ink-500 line-clamp-1 mt-0.5">{g.summary}</p>}
                  </div>
                  <div className="hidden sm:flex items-center gap-1 text-xs text-ink-500 shrink-0">
                    <Heart size={12} className="text-accent-500 fill-accent-500" /> {g.likeCount}
                  </div>
                </HoverCard>
              </Link>
            ))
          )}

          {tab === 'characters' && (
            characters.length === 0 ? <Empty text="暂无英雄角色数值数据" /> : <CharacterStatsTab characters={characters} />
          )}

          {tab === 'weapons' && (
            weapons.length === 0 ? <Empty text="暂无武器装备数值数据" /> : <WeaponStatsTab weapons={weapons} />
          )}

          {tab === 'artifacts' && (
            artifacts.length === 0 ? <Empty text="暂无圣遗物套装数据" /> : <ArtifactStatsTab artifacts={artifacts} />
          )}

          {tab === 'mechanics' && (
            mechanics.length === 0 ? <Empty text="暂无底层战斗机制数据" /> : <MechanicRulesTab mechanics={mechanics} />
          )}

          {tab === 'news' && (
            articles.length === 0 ? <Empty text="暂无资讯" /> : articles.map((a) => (
              <HoverCard key={a.id} className="p-4">
                <div className="flex items-center gap-2 mb-1">
                  {a.category && <Tag size="sm">{a.category}</Tag>}
                  {a.publishedAt && <span className="text-xs text-ink-500">{new Date(a.publishedAt).toLocaleDateString()}</span>}
                </div>
                <h3 className="text-base font-medium text-ink-900">{a.title}</h3>
                {a.content && <p className="text-sm text-ink-500 line-clamp-2 mt-1">{a.content}</p>}
              </HoverCard>
            ))
          )}

          {tab === 'wiki' && (
            wiki.length === 0 ? <Empty text="暂无百科" /> : wiki.map((w) => (
              <WikiCard key={w.id} entry={w} />
            ))
          )}

          {tab === 'qa' && (
            questions.length === 0 ? <Empty text="暂无讨论" /> : questions.map((q) => (
              <Link key={q.id} to={`/qa`}>
                <HoverCard className="p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <Tag size="sm" variant="outline">问答</Tag>
                    <span className="text-xs text-ink-500">{new Date(q.createdAt).toLocaleDateString()}</span>
                  </div>
                  <h3 className="text-base font-medium text-ink-900">{q.title}</h3>
                  {q.description && <p className="text-sm text-ink-500 line-clamp-2 mt-1">{q.description}</p>}
                </HoverCard>
              </Link>
            ))
          )}
        </div>
      </section>
    </div>
  )
}

function WikiCard({ entry }: { entry: WikiEntry }) {
  const [expanded, setExpanded] = useState(false)
  const title = entry.title || ''
  const tagMatch = title.match(/^[【\[](.+?)[】\]]/)
  const categoryTag = tagMatch ? tagMatch[1] : null
  const cleanTitle = tagMatch ? title.slice(tagMatch[0].length).trim() : title

  const renderContent = (text: string) => {
    if (!text) return null
    const lines = text.split('\n')
    const elements: React.ReactNode[] = []
    let inTable = false
    let tableHeaders: string[] = []
    let tableRows: string[][] = []

    const flushTable = () => {
      if (tableHeaders.length > 0 || tableRows.length > 0) {
        elements.push(
          <div key={`table-${elements.length}`} className="my-3 overflow-x-auto rounded-xl border border-ink-100/60 shadow-xs">
            <table className="w-full text-left text-xs md:text-sm border-collapse">
              {tableHeaders.length > 0 && (
                <thead className="bg-accent-50/80 text-ink-800 font-semibold border-b border-ink-100/60">
                  <tr>
                    {tableHeaders.map((th, idx) => (
                      <th key={idx} className="px-3 py-2 whitespace-nowrap">{th.trim()}</th>
                    ))}
                  </tr>
                </thead>
              )}
              <tbody className="divide-y divide-ink-100/40 bg-surface">
                {tableRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-accent-50/30 transition-colors">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-3 py-2 text-ink-700 whitespace-nowrap">{cell.trim()}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      }
      tableHeaders = []
      tableRows = []
      inTable = false
    }

    lines.forEach((line, index) => {
      const trimmed = line.trim()
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        inTable = true
        const cells = trimmed.slice(1, -1).split('|')
        if (cells.every((c) => /^[\s\-:]+$/.test(c))) {
          return
        }
        if (tableHeaders.length === 0) {
          tableHeaders = cells
        } else {
          tableRows.push(cells)
        }
      } else {
        if (inTable) flushTable()
        if (trimmed.startsWith('###')) {
          elements.push(
            <h4 key={index} className="text-sm font-semibold text-ink-900 mt-2 mb-1">
              {trimmed.replace(/^###+\s*/, '')}
            </h4>
          )
        } else if (trimmed.startsWith('- **')) {
          const boldMatch = trimmed.match(/^- \*\*(.+?)\*\*[:：]?\s*(.*)$/)
          if (boldMatch) {
            elements.push(
              <div key={index} className="text-xs md:text-sm text-ink-600 my-0.5 flex gap-1">
                <span className="font-semibold text-ink-800 shrink-0">{boldMatch[1]}：</span>
                <span>{boldMatch[2]}</span>
              </div>
            )
          } else {
            elements.push(<p key={index} className="text-xs md:text-sm text-ink-600 my-0.5">{trimmed.slice(2)}</p>)
          }
        } else if (trimmed.length > 0) {
          elements.push(<p key={index} className="text-xs md:text-sm text-ink-600 my-1">{trimmed}</p>)
        }
      }
    })

    if (inTable) flushTable()
    return elements
  }

  const isNumericStat = categoryTag && (categoryTag.includes('属性') || categoryTag.includes('数值') || categoryTag.includes('机制') || categoryTag.includes('图鉴'))

  return (
    <HoverCard className="p-5 transition-all">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          {categoryTag && (
            <Tag size="sm" variant={categoryTag.includes('角色') ? 'solid' : (categoryTag.includes('装备') || categoryTag.includes('兵刃') ? 'soft' : 'outline')}>
              {categoryTag}
            </Tag>
          )}
          <h3 className="text-base font-semibold text-ink-900 flex items-center gap-2">
            <BookOpen size={16} className="text-accent-500 shrink-0" />
            {cleanTitle || title}
          </h3>
        </div>
        {entry.content && entry.content.length > 200 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-accent-600 hover:text-accent-700 shrink-0 font-medium py-1 px-2 rounded-lg hover:bg-accent-50 transition-colors"
          >
            {expanded ? '收起面板' : '展开数值'}
          </button>
        )}
      </div>

      <div className={`mt-2 ${!expanded && isNumericStat && entry.content && entry.content.length > 300 ? 'max-h-36 overflow-hidden relative' : ''}`}>
        {renderContent(entry.content || '')}
        {!expanded && isNumericStat && entry.content && entry.content.length > 300 && (
          <div className="absolute inset-x-0 bottom-0 h-14 bg-gradient-to-t from-white to-transparent pointer-events-none" />
        )}
      </div>
    </HoverCard>
  )
}

function Empty({ text }: { text: string }) {
  return <div className="text-center py-14 text-ink-500">{text}</div>
}
