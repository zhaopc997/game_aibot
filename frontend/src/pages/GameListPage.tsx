import { Link, useSearchParams } from 'react-router-dom'
import { Search, Filter } from 'lucide-react'
import { useState, useEffect } from 'react'
import { HoverCard } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'
import { Input } from '@/components/ui/Input'
import { GameCover } from '@/components/GameCover'
import client, { unwrap } from '@/api/client'

interface Game {
  id: number
  name: string
  alias?: string
  platform?: string
  category?: string
  description?: string
  currentVersion?: string
  coverUrl?: string | null
}

const FALLBACK_GAMES: Game[] = [
  { id: 2, name: '原神', category: '开放世界', platform: 'PC/移动/PS', currentVersion: '5.0', description: '米哈游自研开放世界冒险 RPG' },
  { id: 26, name: '鸣潮', category: '开放世界', platform: 'PC/iOS/Android', currentVersion: '1.3', coverUrl: null, description: '库洛游戏自研开放世界动作大作，滑翔飞檐走壁、协奏变奏连携与弹刀博弈。' },
  { id: 8, name: '崩坏：星穹铁道', category: 'RPG', platform: 'PC/移动/PS5', currentVersion: '2.7', description: '银河冒险策略回合制 RPG' },
  { id: 4, name: '黑神话：悟空', category: 'ARPG', platform: 'PC/PS5', currentVersion: '1.0', description: '以西游神话为背景的国产 3A 动作角色扮演游戏' },
  { id: 24, name: '王者荣耀', category: 'MOBA', platform: '移动端 (iOS/Android)', currentVersion: 'S36', coverUrl: null, description: '腾讯天美工作室研发的国民级 5v5 团队公平竞技手游，海量英雄、平衡对抗与经典出装铭文体系。' },
  { id: 25, name: '绝区零', category: 'ARPG', platform: 'PC/移动/PS5', currentVersion: '1.2', coverUrl: null, description: '米哈游全新 3D 动作游戏，潮酷现代都市、极爽极限闪避招架与失衡连携混沌异常机制。' },
  { id: 17, name: 'Valorant', category: 'FPS', platform: 'PC', currentVersion: '9.06', coverUrl: null, description: '拳头游戏 5v5 战术射击竞技力作，特工技能配合急停枪法，爆头一枪毙命与精密经济博弈。' },
  { id: 20, name: '永劫无间', category: '动作', platform: 'PC/主机/移动', currentVersion: 'Season 14', coverUrl: null, description: '网易国风武侠动作吃鸡，冷热兵器博弈、飞索走位与剪刀石头布振刀机制。' },
  { id: 11, name: '博德之门3', category: 'CRPG', platform: 'PC/PS5/Xbox', currentVersion: 'Patch 7', coverUrl: null, description: '拉瑞安工作室开发的 TGA 年度最佳神作，D&D 5e 规则、起源同伴深度叙事与无限可能。' },
  { id: 10, name: '暗黑破坏神4', category: 'ARPG', platform: 'PC/PS/Xbox', currentVersion: '2.0.4', coverUrl: null, description: '暴雪出品的暗黑奇幻动作刷宝 RPG，六大职业构筑、暗金神话与深坑冲层。' },
  { id: 6, name: '英雄联盟', category: 'MOBA', platform: 'PC', currentVersion: '14.19', description: '拳头游戏风靡全球的 5v5 战术竞技游戏' },
  { id: 5, name: 'DOTA 2', category: 'MOBA', platform: 'PC', currentVersion: '7.37d', coverUrl: null, description: 'V社全球顶级多人战术竞技游戏，深度正反补、高低地视野与百名英雄博弈。' },
  { id: 1, name: '艾尔登法环', category: 'RPG', platform: 'PS5/Xbox/PC', currentVersion: '1.10', description: 'FromSoftware 魂系开放世界巅峰神作' },
  { id: 3, name: '塞尔达传说：王国之泪', category: '冒险', platform: 'Switch', currentVersion: '1.2.1', description: '任天堂划时代开放世界动作冒险巨作' },
  { id: 9, name: '明日方舟', category: '塔防', platform: '移动端', currentVersion: '2.3.0', coverUrl: null, description: '鹰角网络策略自走与战术塔防 RPG，指挥罗德岛各职阶干员应对矿石病与天灾危机。' },
  { id: 13, name: '荒野大镖客2', category: '开放世界', platform: 'PC/PS/Xbox', currentVersion: '1.32', description: 'Rockstar 巅峰级西部开放世界史诗巨作，拟真生态与死神之眼极速拔枪。' },
  { id: 14, name: '空洞骑士', category: '类银河恶魔城', platform: 'PC/Switch/PS/Xbox', currentVersion: '1.5.78', description: 'Team Cherry 现象级类银河恶魔城手绘神作，衰落虫之王国、骨钉剑技与深渊暗影法术。' },
  { id: 15, name: '以撒的结合：忏悔', category: 'Rougelike', platform: 'PC/主机', currentVersion: 'Repentance+', description: '肉鸽地牢射击开拓级神作，道具异能组合变身与硫磺火血泪清洗地牢。' },
  { id: 18, name: '炉石传说', category: '卡牌', platform: 'PC/移动', currentVersion: '30.4', description: '暴雪出品的全球风靡集换式卡牌对战游戏，精妙水晶曲线、战吼亡语与宇宙套牌。' },
  { id: 21, name: '幻塔', category: '开放世界', platform: 'PC/移动/主机', currentVersion: '3.8', description: '完美世界轻科幻开放世界手游，拟态角色与幻想时间时停机制。' },
  { id: 22, name: 'Phasmophobia', category: '恐怖', platform: 'PC/VR/主机', currentVersion: 'v0.10', description: '4人联机心理恐怖调查神作，探测设备识别幽灵种类并存活撤离。' },
  { id: 23, name: '火线战姬', category: '机甲射击', platform: 'PC/移动', currentVersion: 'v1.2', description: '高科技机甲战姬少女动作射击，抵御机械异变浪潮。' },
  { id: 27, name: '和平精英', category: '战术竞技', platform: '移动端', currentVersion: '1.27', coverUrl: null, description: '腾讯光子国民级战术竞技射击手游，百人同场竞技与真实弹道射击。' },
  { id: 28, name: '金铲铲之战', category: '自走棋', platform: '移动端', currentVersion: 'S12', coverUrl: null, description: '腾讯官方授权的正版自走棋手游，八人同台博弈与海克斯强化。' },
  { id: 29, name: '阴阳师', category: 'RPG', platform: '移动端/PC', currentVersion: 'v1.7', coverUrl: null, description: '网易旗舰和风回合制 RPG 手游，人鬼共生平安时代与深度御魂养成。' },
  { id: 30, name: '崩坏3', category: 'ARPG', platform: 'PC/移动端', currentVersion: 'v7.8', coverUrl: null, description: '米哈游 3D 全视角动作手游，时空断裂与次世代打击感。' },
  { id: 31, name: '重返未来：1999', category: 'RPG', platform: 'PC/移动端', currentVersion: 'v2.2', coverUrl: null, description: '深蓝互动复古神秘学策略 RPG 手游，穿梭暴雨倒退探寻历史真相。' },
  { id: 32, name: '指尖像素城', category: '放置卡牌RPG', platform: '移动端 (微信小游戏/iOS/Android)', currentVersion: 'V2.4.0', coverUrl: '/games/pixel_city/cover.svg', description: '超人气像素风策略放置卡牌手游，神明与虚空神将、阵奕布阵、怒气压制与专属圣物。' },
  { id: 7, name: 'CS2', category: 'FPS', platform: 'PC', currentVersion: '1.39', description: 'V社全球顶级战术第一人称射击游戏，起源2引擎动态体积烟雾与亚毫秒级 Sub-tick 物理判定。' },
]

export default function GameListPage() {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const cat = params.get('cat') ?? '全部'
  const [draft, setDraft] = useState(q)
  const [games, setGames] = useState<Game[]>(FALLBACK_GAMES)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    client.get('/games')
      .then((r) => {
        const list = unwrap<Game[]>(r)
        if (Array.isArray(list) && list.length > 0) {
          setGames(list)
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const categories: string[] = ['全部', ...Array.from(new Set(games.map((g) => g.category).filter((c): c is string => !!c)))]

  const filtered = games.filter(
    (g) => (cat === '全部' || g.category === cat) && g.name.includes(q)
  )

  return (
    <div className="pt-10 pb-20">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-semibold text-ink-900">游戏库</h1>
        <p className="mt-1 text-sm text-ink-500">探索 {games.length} 款游戏,寻找你的下一段冒险</p>
      </div>

      {/* 搜索 + 筛选 */}
      <div className="flex flex-col md:flex-row gap-3 mb-8">
        <form
          onSubmit={(e) => { e.preventDefault(); setParams({ q: draft, cat }) }}
          className="flex-1 relative"
        >
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-300 pointer-events-none" />
          <Input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="搜索游戏名…"
            className="pl-10"
          />
        </form>
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin">
          <Filter size={14} className="text-ink-500 shrink-0" />
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setParams({ q, cat: c })}
              className={`shrink-0 h-9 px-3.5 rounded-xl text-sm font-medium transition-all ${
                cat === c
                  ? 'bg-accent-500 text-white shadow-soft'
                  : 'bg-surface text-ink-700 border border-ink-100 hover:border-ink-300'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* 游戏网格 */}
      {loading ? (
        <div className="text-center py-16 text-ink-500">加载中…</div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {filtered.map((g) => (
            <Link key={g.id} to={`/games/${g.id}`}>
              <HoverCard className="p-5">
                <div className="aspect-square rounded-2xl bg-gradient-to-br from-accent-100 to-canvas grid place-items-center overflow-hidden mb-4 shadow-sm border border-ink-100/40">
                  <GameCover
                    src={g.coverUrl}
                    gameId={g.id}
                    alt={g.name}
                    className="h-full w-full"
                  />
                </div>
                <h3 className="text-base font-medium text-ink-900">{g.name}</h3>
                <div className="mt-2 flex items-center gap-1.5">
                  {g.currentVersion && <Tag size="sm">v{g.currentVersion}</Tag>}
                  {g.category && <Tag size="sm" variant="outline">{g.category}</Tag>}
                </div>
              </HoverCard>
            </Link>
          ))}
          {filtered.length === 0 && (
            <div className="col-span-full text-center py-16 text-ink-500">
              没找到符合条件的游戏
            </div>
          )}
        </div>
      )}
    </div>
  )
}
