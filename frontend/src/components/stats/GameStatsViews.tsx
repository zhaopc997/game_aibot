import { useState, useMemo } from 'react'
import { ChevronRight, Search, RotateCcw } from 'lucide-react'
import { Tag } from '@/components/ui/Tag'
import { HoverCard } from '@/components/ui/Card'
import { CharacterDetailModal, CharacterData } from './CharacterDetailModal'
import { WeaponDetailModal } from './WeaponDetailModal'
import { ArtifactDetailModal } from './ArtifactDetailModal'

export type { CharacterData }
export type { LevelStat, RefinementEffect } from './types'
import type { RefinementEffect } from './types'

export interface WeaponData {
  /** 所属游戏 id（后端部分接口未返回，故可选） */
  gameId?: number
  id: number
  name: string
  type: string
  rarity: number
  iconUrl?: string
  baseAtkCurve: { level: string; atk: number }[]
  subStat: {
    stat_name: string
    values: Record<string, string>
    /** 部分游戏的属性以"评级"形式给出 */
    ratings?: string
    /** 部分游戏的属性以"需求"形式给出 */
    requirements?: string
  }
  /** 后端对多数游戏返回数组；少数游戏返回单个对象，故为联合类型 */
  refinements: { rank: string; desc: string }[] | RefinementEffect
  ascensionMaterials?:
    | { tier?: string; items?: string; type?: string; name?: string }[]
    | { tier?: string; items?: string; type?: string; name?: string; catalyst_list?: string }
}

/**
 * 套装的规则/说明信息。
 * 字段因游戏而异，且部分字段值为嵌套结构，故按实际使用点显式声明，
 * 而不是用 Record<string, any> 一笔带过。
 */
export interface ArtifactRulesReference {
  /** 套装定位/类型说明 */
  type?: string
  /** 符文主系（英雄联盟） */
  primary_tree?: string
  /** 推荐适配（英雄/干员/代理人） */
  recommended_for?: string
  /** 4/5 星副词条档位：{ 属性名: [档位1, 档位2, ...] } */
  sub_stat_tiers_4star_and_5star?: Record<string, string[]>
}

export interface ArtifactData {
  /** 所属游戏 id（后端部分接口未返回，故可选） */
  gameId?: number
  id: number
  name: string
  rarityMin: number
  rarityMax: number
  iconUrl?: string
  twoPieceBonus: string
  fourPieceBonus: string
  pieces: { slot: string; name: string; main_stat_rule: string; icon_url?: string }[]
  rulesReference?: ArtifactRulesReference
}

export interface MechanicRuleData {
  id: number
  category: string
  title: string
  formula?: string
  parameters: Record<string, unknown>
}

// -------------------------------------------------------------
// 1. 角色列表视图 (CharacterStatsTab)
// -------------------------------------------------------------
export function CharacterStatsTab({ characters }: { characters: CharacterData[] }) {
  const [search, setSearch] = useState('')
  const [selectedElement, setSelectedElement] = useState<string>('ALL')
  const [selectedRarity, setSelectedRarity] = useState<number | 'ALL'>('ALL')
  const [selectedWeapon, setSelectedWeapon] = useState<string>('ALL')
  const [activeChar, setActiveChar] = useState<CharacterData | null>(null)

  const isHok = useMemo(() => {
    return characters.some((c) => c.gameId === 24 || c.region?.includes('王者大陆') || ['发育路', '对抗路', '打野', '中路', '游走'].includes(c.weaponType))
  }, [characters])

  const isArknights = useMemo(() => {
    return characters.some((c) => c.gameId === 9 || c.region?.includes('罗德岛') || c.element?.includes('近卫') || c.element?.includes('狙击') || c.element?.includes('术师') || c.element?.includes('医疗') || c.baseStats?.[0]?.level?.includes('精0'))
  }, [characters])

  const isZzz = useMemo(() => {
    return characters.some((c) => c.gameId === 25 || c.region?.includes('新艾利都') || c.element?.includes('强攻') || c.element?.includes('击破') || c.element?.includes('异常') || c.element?.includes('防护'))
  }, [characters])

  const isLol = useMemo(() => {
    if (isHok) return false
    return characters.some((c) => ['战士', '法师', '刺客', '射手', '坦克', '辅助'].includes(c.element))
  }, [characters, isHok])

  const isHsr = useMemo(() => {
    return characters.some((c) => ['毁灭', '巡猎', '智识', '同谐', '虚无', '存护', '丰饶', '记忆', '欢愉'].includes(c.weaponType))
  }, [characters])

  const isWukong = useMemo(() => {
    return characters.some((c) => ['劈棍法', '立棍法', '戳棍法', '禁字法', '身外身法', '大圣神威'].includes(c.element))
  }, [characters])

  const isEldenRing = useMemo(() => {
    return characters.some((c) => ['力信流派', '出血流派', '智力法术', '纯物理纯力', '智敏魔武', '感应龙飨', '全能基准'].includes(c.element) || c.name?.includes('褪色者'))
  }, [characters])

  const isZelda = useMemo(() => {
    return characters.some((c) => ['时空突击', '左纳乌工程', '潜行暗杀', '元素魔法', '高空气流', '神圣誓约'].includes(c.element) || c.name?.includes('林克'))
  }, [characters])

  const isNaraka = useMemo(() => {
    return characters.some((c) => c.gameId === 20 || c.region?.includes('聚窟洲') || c.region?.includes('火罗国') || c.element?.includes('真气') || c.element?.includes('无极') || c.weaponType?.includes('长剑') || c.weaponType?.includes('太刀') || c.weaponType?.includes('阔刀'))
  }, [characters])

  const availableElements = useMemo(() => {
    const set = new Set<string>()
    characters.forEach((c) => {
      if (c.element) set.add(c.element)
    })
    return ['ALL', ...Array.from(set)]
  }, [characters])

  const availableWeapons = useMemo(() => {
    const set = new Set<string>()
    characters.forEach((c) => {
      if (c.weaponType) set.add(c.weaponType)
    })
    return ['ALL', ...Array.from(set)]
  }, [characters])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return characters
      .filter((c) => {
        if (selectedElement !== 'ALL' && c.element !== selectedElement) return false
        if (selectedRarity !== 'ALL' && c.rarity !== selectedRarity) return false
        if (selectedWeapon !== 'ALL' && c.weaponType !== selectedWeapon) return false
        if (q) {
          const matchName = c.name?.toLowerCase().includes(q)
          const matchTitle = c.title?.toLowerCase().includes(q)
          const matchRegion = c.region?.toLowerCase().includes(q)
          const matchWeapon = c.weaponType?.toLowerCase().includes(q)
          if (!matchName && !matchTitle && !matchRegion && !matchWeapon) return false
        }
        return true
      })
      .sort((a, b) => {
        // 5-star / 6-star first, then by name
        if (b.rarity !== a.rarity) return b.rarity - a.rarity
        return a.name.localeCompare(b.name, 'zh-CN')
      })
  }, [characters, search, selectedElement, selectedRarity, selectedWeapon])

  const isFiltered = search !== '' || selectedElement !== 'ALL' || selectedRarity !== 'ALL' || selectedWeapon !== 'ALL'

  const resetFilters = () => {
    setSearch('')
    setSelectedElement('ALL')
    setSelectedRarity('ALL')
    setSelectedWeapon('ALL')
  }

  const elementColorMap: Record<string, { bg: string; text: string; badge: string }> = {
    水: { bg: 'from-blue-50/80 to-canvas', text: 'text-blue-700', badge: 'bg-blue-100 text-blue-800' },
    火: { bg: 'from-red-50/80 to-canvas', text: 'text-red-700', badge: 'bg-red-100 text-red-800' },
    风: { bg: 'from-emerald-50/80 to-canvas', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-800' },
    雷: { bg: 'from-purple-50/80 to-canvas', text: 'text-purple-700', badge: 'bg-purple-100 text-purple-800' },
    草: { bg: 'from-green-50/80 to-canvas', text: 'text-green-700', badge: 'bg-green-100 text-green-800' },
    冰: { bg: 'from-cyan-50/80 to-canvas', text: 'text-cyan-700', badge: 'bg-cyan-100 text-cyan-800' },
    岩: { bg: 'from-amber-50/80 to-canvas', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' },
    // 绝区零属性
    '冰属性·强攻': { bg: 'from-cyan-50/80 to-canvas', text: 'text-cyan-700', badge: 'bg-cyan-100 text-cyan-800' },
    '以太属性·强攻': { bg: 'from-fuchsia-50/80 to-canvas', text: 'text-fuchsia-700', badge: 'bg-fuchsia-100 text-fuchsia-800' },
    '物理属性·异常': { bg: 'from-amber-50/80 to-canvas', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' },
    '电属性·击破': { bg: 'from-purple-50/80 to-canvas', text: 'text-purple-700', badge: 'bg-purple-100 text-purple-800' },
    '火属性·防护': { bg: 'from-red-50/80 to-canvas', text: 'text-red-700', badge: 'bg-red-100 text-red-800' },
    '火属性·异常': { bg: 'from-orange-50/80 to-canvas', text: 'text-orange-700', badge: 'bg-orange-100 text-orange-800' },
    // 明日方舟职业
    '近卫·法战': { bg: 'from-red-50/80 to-canvas', text: 'text-red-700', badge: 'bg-red-100 text-red-800' },
    '近卫·解放者': { bg: 'from-amber-50/80 to-canvas', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' },
    '狙击·投掷手': { bg: 'from-orange-50/80 to-canvas', text: 'text-orange-700', badge: 'bg-orange-100 text-orange-800' },
    '医疗·咒愈师': { bg: 'from-emerald-50/80 to-canvas', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-800' },
    // MOBA 职业定位 (王者荣耀 & LOL)
    战士: { bg: 'from-orange-50/80 to-canvas', text: 'text-orange-700', badge: 'bg-orange-100 text-orange-800' },
    法师: { bg: 'from-indigo-50/80 to-canvas', text: 'text-indigo-700', badge: 'bg-indigo-100 text-indigo-800' },
    刺客: { bg: 'from-rose-50/80 to-canvas', text: 'text-rose-700', badge: 'bg-rose-100 text-rose-800' },
    射手: { bg: 'from-amber-50/80 to-canvas', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' },
    坦克: { bg: 'from-emerald-50/80 to-canvas', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-800' },
    辅助: { bg: 'from-teal-50/80 to-canvas', text: 'text-teal-700', badge: 'bg-teal-100 text-teal-800' },
    // 永劫无间 真气与武学流派
    '阴阳真气 · 控场': { bg: 'from-purple-50/80 to-canvas', text: 'text-purple-700', badge: 'bg-purple-100 text-purple-800' },
    '烈焰真气 · 狂战': { bg: 'from-red-50/80 to-canvas', text: 'text-red-700', badge: 'bg-red-100 text-red-800' },
    '玄冰真气 · 隐刺': { bg: 'from-cyan-50/80 to-canvas', text: 'text-cyan-700', badge: 'bg-cyan-100 text-cyan-800' },
    '神圣真气 · 护持': { bg: 'from-amber-50/80 to-canvas', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' },
    '金刚怒目 · 巨盾': { bg: 'from-emerald-50/80 to-canvas', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-800' },
    '幻惑妖气 · 控场': { bg: 'from-pink-50/80 to-canvas', text: 'text-pink-700', badge: 'bg-pink-100 text-pink-800' },
    '沙暴真气 · 控场': { bg: 'from-yellow-50/80 to-canvas', text: 'text-yellow-700', badge: 'bg-yellow-100 text-yellow-800' },
    '沧海狂浪 · 狂战': { bg: 'from-blue-50/80 to-canvas', text: 'text-blue-700', badge: 'bg-blue-100 text-blue-800' },
    '雷霆真气 · 刺客': { bg: 'from-indigo-50/80 to-canvas', text: 'text-indigo-700', badge: 'bg-indigo-100 text-indigo-800' },
    '草木真气 · 游侠': { bg: 'from-green-50/80 to-canvas', text: 'text-green-700', badge: 'bg-green-100 text-green-800' },
    '机械偃术 · 战术': { bg: 'from-slate-50/80 to-canvas', text: 'text-slate-700', badge: 'bg-slate-100 text-slate-800' },
    '天命真气 · 刺客': { bg: 'from-violet-50/80 to-canvas', text: 'text-violet-700', badge: 'bg-violet-100 text-violet-800' },
    '幽冥鬼火 · 刺客': { bg: 'from-fuchsia-50/80 to-canvas', text: 'text-fuchsia-700', badge: 'bg-fuchsia-100 text-fuchsia-800' },
    '金刚真气 · 巨坦': { bg: 'from-amber-50/80 to-canvas', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' },
    '乾坤真气 · 控场': { bg: 'from-teal-50/80 to-canvas', text: 'text-teal-700', badge: 'bg-teal-100 text-teal-800' },
  }

  return (
    <div className="space-y-6">
      {/* Search & Filter Header */}
      <div className="p-4 rounded-2xl bg-surface border border-ink-100 space-y-3.5 shadow-xs">
        {/* Row 1: Search and Counts */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={
                isNaraka
                  ? "搜索英雄豪杰名称、称号、武学真气 (如: 宁红夜、特木尔、迦南、季沧海)..."
                  : isHok
                  ? "搜索王者英雄名称、称号、阵营 (如: 孙悟空、公孙离、诸葛亮)..."
                  : isArknights
                  ? "搜索干员代号、职业分支、所属势力 (如: 史尔特尔、玛恩纳、维什戴尔)..."
                  : isZzz
                  ? "搜索代理人名称、阵营、特性 (如: 艾莲、朱鸢、简、青衣)..."
                  : "搜索角色名称、称号、所属地区 (如: 那维莱特、亚索、艾欧尼亚)..."
              }
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-canvas border border-ink-100 text-ink-900 placeholder:text-ink-400 focus:outline-none focus:border-accent-500 transition-colors"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-ink-400 hover:text-ink-700"
              >
                ✕
              </button>
            )}
          </div>
          <div className="flex items-center gap-2 justify-between sm:justify-end text-xs">
            <span className="text-ink-500 font-medium">
              共 <strong className="text-ink-900 font-bold">{characters.length}</strong>{' '}
              {isNaraka ? '位英雄豪杰' : isArknights ? '位干员' : isZzz ? '位代理人' : isHok || isLol ? '位英雄' : '位角色'}，当前展示{' '}
              <strong className="text-accent-600 font-bold">{filtered.length}</strong> 位
            </span>
            {isFiltered && (
              <button
                onClick={resetFilters}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-ink-600 hover:text-ink-900 bg-ink-100/70 hover:bg-ink-200/80 transition-colors font-medium text-[11px]"
              >
                <RotateCcw size={12} /> 重置筛选
              </button>
            )}
          </div>
        </div>

        {/* Row 2: Element / Role Filter */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          <span className="text-xs font-semibold text-ink-500 mr-1 shrink-0">
            {isNaraka ? '武学流派:' : isHok ? '英雄定位:' : isArknights ? '职阶分类:' : isZzz ? '特性分类:' : isLol ? '职业定位:' : isHsr ? '战斗属性:' : isWukong ? '武学流派:' : isEldenRing ? '构筑流派:' : isZelda ? '能力形态:' : '元素分类:'}
          </span>
          {availableElements.map((elem) => (
            <button
              key={elem}
              onClick={() => setSelectedElement(elem)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all shrink-0 ${
                selectedElement === elem
                  ? 'bg-ink-900 text-white shadow-soft font-semibold'
                  : 'bg-canvas text-ink-600 hover:bg-ink-100/80 border border-ink-100/60'
              }`}
            >
              {elem === 'ALL'
                ? isNaraka ? '全部流派' : isHok ? '全部定位' : isArknights ? '全部职阶' : isZzz ? '全部特性' : isLol ? '全部定位' : isHsr ? '全部属性' : isWukong ? '全部流派' : isEldenRing ? '全部构筑' : isZelda ? '全部形态' : '全部元素'
                : isNaraka || isHok || isArknights || isZzz || isLol || isWukong || isEldenRing || isZelda ? elem : isHsr ? `${elem}属性` : `${elem}元素`}
            </button>
          ))}
        </div>

        {/* Row 3: Weapon & Rarity Filter */}
        <div className="flex flex-wrap items-center gap-4 pt-1 border-t border-ink-100/40 text-xs">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="font-semibold text-ink-500 shrink-0">
              {isNaraka ? '擅长神兵:' : isHok ? '推荐分路:' : isArknights ? '职业分支:' : isZzz ? '专属武具:' : isLol ? '攻击方式:' : isHsr ? '命途定位:' : isWukong ? '神兵品级:' : isEldenRing ? '兵刃/触媒:' : isZelda ? '专属武器:' : '武器类型:'}
            </span>
            {availableWeapons.map((w) => (
              <button
                key={w}
                onClick={() => setSelectedWeapon(w)}
                className={`px-2.5 py-1 rounded-lg text-xs transition-colors ${
                  selectedWeapon === w
                    ? 'bg-accent-500 text-white font-semibold'
                    : 'text-ink-600 hover:bg-ink-100/70'
                }`}
              >
                {w === 'ALL' ? '全部' : w}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-ink-500 shrink-0">{isLol || isHok ? '上手难度:' : '稀有度:'}</span>
            {[
              { val: 'ALL', label: '全部' },
              ...(isArknights ? [
                { val: 6, label: '★★★★★★ 六星干员' },
                { val: 5, label: '★★★★★ 五星干员' },
              ] : isZzz ? [
                { val: 5, label: '★★★★★ S 级代理人' },
                { val: 4, label: '★★★★ A 级代理人' },
              ] : isHok ? [
                { val: 5, label: '★★★★★ 顶尖操作' },
                { val: 4, label: '★★★★ 主流进阶' },
                { val: 3, label: '★★★ 新手推荐' },
              ] : isLol ? [
                { val: 5, label: '★★★★★ 精通上限' },
                { val: 4, label: '★★★★ 中等进阶' },
                { val: 3, label: '★★★ 新手推荐' },
              ] : [
                { val: 5, label: '★★★★★ 5星' },
                { val: 4, label: '★★★★ 4星' },
              ]),
            ].map((r) => (
              <button
                key={String(r.val)}
                onClick={() => setSelectedRarity(r.val as number | 'ALL')}
                className={`px-2.5 py-1 rounded-lg text-xs transition-colors ${
                  selectedRarity === r.val
                    ? 'bg-amber-500 text-white font-semibold'
                    : 'text-ink-600 hover:bg-ink-100/70'
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Characters Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-16 bg-surface rounded-3xl border border-ink-100 p-8 space-y-3">
          <div className="text-4xl">🔍</div>
          <h3 className="text-base font-bold text-ink-800">没有找到匹配的角色</h3>
          <p className="text-xs text-ink-500 max-w-sm mx-auto">
            尝试更换搜索关键词，或清除分类、星级与攻击方式筛选条件
          </p>
          <button
            onClick={resetFilters}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-accent-500 text-white shadow-soft hover:bg-accent-600 transition-colors"
          >
            <RotateCcw size={14} /> 清除全部筛选条件
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((c) => {
            const theme = elementColorMap[c.element] || { bg: 'from-accent-50 to-canvas', text: 'text-accent-700', badge: 'bg-accent-100 text-accent-800' }
            const baseStats = c.baseStats || []
            const maxStat = baseStats[baseStats.length - 1]
            const maxLv = maxStat?.level || '90'

            return (
              <HoverCard
                key={c.id}
                onClick={() => setActiveChar(c)}
                className={`p-5 cursor-pointer bg-gradient-to-br ${theme.bg} border border-ink-100/60 hover:shadow-lift transition-all relative overflow-hidden group`}
              >
                <div className="flex items-start gap-4">
                  <div className="h-16 w-16 rounded-2xl bg-surface border-2 border-white shadow-soft overflow-hidden shrink-0 group-hover:scale-105 transition-transform relative">
                    {c.avatarUrl ? (
                      <img
                        src={c.avatarUrl}
                        alt={c.name}
                        onError={(e) => {
                          e.currentTarget.style.display = 'none'
                          const fallback = e.currentTarget.nextElementSibling as HTMLElement
                          if (fallback) fallback.style.display = 'grid'
                        }}
                        className="h-full w-full object-cover"
                      />
                    ) : null}
                    <div
                      style={{ display: c.avatarUrl ? 'none' : 'grid' }}
                      className={`h-full w-full place-items-center font-bold text-xl ${theme.text} bg-surface`}
                    >
                      {c.name.slice(0, 1)}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <h3 className="text-base font-bold text-ink-900 truncate">{c.name}</h3>
                      <span className="text-amber-500 text-xs tracking-wider">{'★'.repeat(c.rarity)}</span>
                    </div>
                    {c.title && <div className="text-xs text-ink-500 truncate">{c.title}</div>}
                    <div className="flex items-center gap-1.5 mt-2 flex-wrap text-xs">
                      <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold ${theme.badge}`}>
                        {c.element}
                      </span>
                      <Tag size="sm" variant="outline">{c.weaponType}</Tag>
                      {c.region && <Tag size="sm" variant="outline">{c.region}</Tag>}
                    </div>
                  </div>
                </div>

                {/* Quick Stat Panel */}
                <div className="mt-4 pt-3 border-t border-ink-100/60 grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="p-1.5 rounded-xl bg-surface/80">
                    <div className="text-[10px] text-ink-400">{isNaraka ? '满级体力' : `${maxLv}级生命`}</div>
                    <div className="font-bold text-ink-800 mt-0.5">{maxStat?.hp || '-'}</div>
                  </div>
                  <div className="p-1.5 rounded-xl bg-surface/80">
                    <div className="text-[10px] text-ink-400">{isNaraka ? '攻击加成' : `${maxLv}级攻击`}</div>
                    <div className="font-bold text-ink-800 mt-0.5">{maxStat?.atk ? `${maxStat.atk}${isNaraka ? '%' : ''}` : '-'}</div>
                  </div>
                  <div className="p-1.5 rounded-xl bg-surface/80">
                    <div className="text-[10px] text-ink-400">
                      {isNaraka ? '护甲 / 精力' : isHok ? '满级物防/魔抗' : isArknights ? '阻挡 / 法抗' : isZzz ? '冲击 / 精通' : isLol ? '满级护甲' : isHsr ? '基础速度' : isWukong ? '气力/法力' : isEldenRing ? '强韧度' : isZelda ? '能源/耐力' : '突破属性'}
                    </div>
                    <div className="font-bold text-accent-700 mt-0.5 truncate">
                      {isNaraka
                        ? `${maxStat?.armor ?? 1250} / ${maxStat?.energy ?? 140}`
                        : isHok
                        ? `${maxStat?.def || '-'} / ${maxStat?.spell_block ?? 169}`
                        : isArknights
                        ? `阻挡 ${maxStat?.block ?? 1} / 法抗 ${maxStat?.res ?? 0}`
                        : isZzz
                        ? `${maxStat?.impact ?? 100} / ${maxStat?.anomaly_proficiency ?? 80}`
                        : isLol
                        ? (maxStat?.def || '-')
                        : isHsr
                        ? `${maxStat?.speed || 100} 点`
                        : isWukong
                        ? `${maxStat?.stamina || '-'}/${maxStat?.mana || '-'}`
                        : isEldenRing
                        ? `${maxStat?.poise || 0} 点`
                        : isZelda
                        ? `${maxStat?.stamina || '-'}`
                        : (c.specialAscensionStat?.stat_name || '-')}
                    </div>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between text-xs font-medium text-accent-700 group-hover:text-accent-800">
                  <span>
                    {isNaraka
                      ? '查看修行数值/武学绝技/印记配装'
                      : isHok
                      ? '查看15级数值/技能连招/出装铭文'
                      : isArknights
                      ? '查看精二白值/专精技能/模组推荐'
                      : isZzz
                      ? '查看60级白值/影画/音擎驱动盘搭配'
                      : isLol
                      ? '查看18级数值/技能QWER/推荐出装'
                      : isHsr
                      ? '查看80级白值/星魂/行迹技能'
                      : isWukong
                      ? '查看流派技能/六根天资/配装'
                      : isEldenRing
                      ? '查看150级属性/战技祷告/护符搭配'
                      : isZelda
                      ? '查看心之容器/神技战法/防具搭配'
                      : '查看全等级/技能/命座数值'}
                  </span>
                  <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                </div>
              </HoverCard>
            )
          })}
        </div>
      )}

      {/* Modal */}
      <CharacterDetailModal character={activeChar} onClose={() => setActiveChar(null)} />
    </div>
  )
}

// -------------------------------------------------------------
// 2. 武器装备视图 (WeaponStatsTab)
// -------------------------------------------------------------
// -------------------------------------------------------------
// 2. 武器装备视图 (WeaponStatsTab)
// -------------------------------------------------------------
export function WeaponStatsTab({ weapons }: { weapons: WeaponData[] }) {
  const [search, setSearch] = useState('')
  const [selectedType, setSelectedType] = useState<string>('ALL')
  const [selectedRarity, setSelectedRarity] = useState<number | 'ALL'>('ALL')
  const [activeWeapon, setActiveWeapon] = useState<WeaponData | null>(null)

  const isHok = useMemo(() => {
    return weapons.some((w) => w.gameId === 24 || w.name?.includes('无尽战刃') || w.name?.includes('破晓') || w.name?.includes('宗师之力') || w.type?.includes('物理输出') || w.type?.includes('打野装备'))
  }, [weapons])

  const isArknights = useMemo(() => {
    return weapons.some((w) => w.gameId === 9 || w.type?.includes('模组') || w.name?.includes('模组') || w.name?.includes('莱瓦汀') || w.name?.includes('未尽之剑'))
  }, [weapons])

  const isZzz = useMemo(() => {
    return weapons.some((w) => w.gameId === 25 || w.type?.includes('音擎') || w.name?.includes('音擎') || w.name?.includes('深海访客') || w.name?.includes('防暴者'))
  }, [weapons])

  const isLol = useMemo(() => {
    if (isHok) return false
    return weapons.some((w) => w.type?.includes('装备') || w.type?.includes('鞋子') || w.baseAtkCurve?.[0]?.level === '合成总价')
  }, [weapons, isHok])

  const isHsr = useMemo(() => {
    return weapons.some((w) => ['毁灭', '巡猎', '智识', '同谐', '虚无', '存护', '丰饶', '记忆', '欢愉'].includes(w.type))
  }, [weapons])

  const isWukong = useMemo(() => {
    return weapons.some((w) => w.type?.includes('神珍') || w.type?.includes('特品') || w.type?.includes('兵刃') || w.name?.includes('金箍棒'))
  }, [weapons])

  const isEldenRing = useMemo(() => {
    return weapons.some((w) => w.name?.includes('亵渎') || w.name?.includes('月隐') || w.name?.includes('暗月') || w.name?.includes('尸山血海'))
  }, [weapons])

  const isZelda = useMemo(() => {
    return weapons.some((w) => w.name?.includes('大师之剑') || w.name?.includes('兽神弓') || w.name?.includes('七宝匕首') || w.name?.includes('近卫双手剑'))
  }, [weapons])

  const isNaraka = useMemo(() => {
    return weapons.some((w) => w.gameId === 20 || w.type?.includes('近战武器') || w.type?.includes('远程武器') || w.name?.includes('太刀') || w.name?.includes('阔刀') || w.name?.includes('斩马刀') || w.name?.includes('长枪') || w.name?.includes('双节棍') || w.name?.includes('鸟铳'))
  }, [weapons])

  const availableTypes = useMemo(() => {
    const set = new Set<string>()
    weapons.forEach((w) => {
      if (w.type) set.add(w.type)
    })
    return ['ALL', ...Array.from(set)]
  }, [weapons])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return weapons
      .filter((w) => {
        if (selectedType !== 'ALL' && w.type !== selectedType) return false
        if (selectedRarity !== 'ALL' && w.rarity !== selectedRarity) return false
        if (q) {
          const matchName = w.name?.toLowerCase().includes(q)
          const matchType = w.type?.toLowerCase().includes(q)
          const matchSub = w.subStat?.stat_name?.toLowerCase().includes(q)
          if (!matchName && !matchType && !matchSub) return false
        }
        return true
      })
      .sort((a, b) => {
        if (b.rarity !== a.rarity) return b.rarity - a.rarity
        return a.name.localeCompare(b.name, 'zh-CN')
      })
  }, [weapons, search, selectedType, selectedRarity])

  const isFiltered = search !== '' || selectedType !== 'ALL' || selectedRarity !== 'ALL'

  const resetFilters = () => {
    setSearch('')
    setSelectedType('ALL')
    setSelectedRarity('ALL')
  }

  const rarityColorMap: Record<number, { bg: string; text: string; badge: string }> = {
    5: { bg: 'from-amber-500/10 to-canvas', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' },
    4: { bg: 'from-purple-500/10 to-canvas', text: 'text-purple-700', badge: 'bg-purple-100 text-purple-800' },
    3: { bg: 'from-blue-500/10 to-canvas', text: 'text-blue-700', badge: 'bg-blue-100 text-blue-800' },
    2: { bg: 'from-emerald-500/10 to-canvas', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-800' },
    1: { bg: 'from-ink-500/10 to-canvas', text: 'text-ink-700', badge: 'bg-ink-100 text-ink-800' },
  }

  return (
    <div className="space-y-6">
      {/* Search & Filter Header */}
      <div className="p-4 rounded-2xl bg-surface border border-ink-100 space-y-3.5 shadow-xs">
        {/* Row 1: Search and Counts */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={
                isNaraka
                  ? "搜索神兵武备名称、类型或招式专属机制 (如: 太刀、阔刀、长枪、鸟铳、五眼铳)..."
                  : isHok
                  ? "搜索局内装备名称、类型或被动属性 (如: 无尽战刃、破晓、贤者之书)..."
                  : isArknights
                  ? "搜索专属模组名称、干员代号或特性 (如: 莱瓦汀、未尽之剑、SUR-X)..."
                  : isZzz
                  ? "搜索音擎名称、类型或高级属性 (如: 深海访客、防暴者、淬火钳工)..."
                  : isLol
                  ? "搜索装备名称、类型或属性 (如: 无尽之刃、物理攻击、灭世者)..."
                  : isHsr
                  ? "搜索光锥名称、命途或特效 (如: 行于流逝的岸、虚无、暴伤)..."
                  : isWukong
                  ? "搜索兵刃名称、品阶或妙用 (如: 如意金箍棒、神珍、识破)..."
                  : isEldenRing
                  ? "搜索神兵触媒、类型或战技 (如: 亵渎圣剑、暗月、名刀月隐)..."
                  : isZelda
                  ? "搜索神兵余料、类型或词缀 (如: 大师之剑、兽神弓、七宝匕首)..."
                  : "搜索武器名称、类型或副词条 (如: 护摩之杖、暴击伤害、西风)..."
              }
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-canvas border border-ink-100 text-ink-900 placeholder:text-ink-400 focus:outline-none focus:border-accent-500 transition-colors"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-ink-400 hover:text-ink-700"
              >
                ✕
              </button>
            )}
          </div>
          <div className="flex items-center gap-2 justify-between sm:justify-end text-xs">
            <span className="text-ink-500 font-medium">
              共 <strong className="text-ink-900 font-bold">{weapons.length}</strong>{' '}
              {isNaraka ? '件神兵武备' : isHok ? '件装备' : isArknights ? '件专属模组' : isZzz ? '件音擎' : isLol ? '件装备' : isHsr ? '个光锥' : isWukong ? '件兵刃' : '把武器'}，当前展示{' '}
              <strong className="text-accent-600 font-bold">{filtered.length}</strong>{' '}
              {isNaraka || isHok || isLol || isWukong || isArknights ? '件' : isZzz || isHsr ? '个' : '把'}
            </span>
            {isFiltered && (
              <button
                onClick={resetFilters}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-ink-600 hover:text-ink-900 bg-ink-100/70 hover:bg-ink-200/80 transition-colors font-medium text-[11px]"
              >
                <RotateCcw size={12} /> 重置筛选
              </button>
            )}
          </div>
        </div>

        {/* Row 2: Type & Rarity Filter */}
        <div className="flex flex-wrap items-center gap-4 pt-1 border-t border-ink-100/40 text-xs">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="font-semibold text-ink-500 shrink-0">
              {isHok ? '装备分类:' : isArknights ? '模组分类:' : isZzz ? '音擎分类:' : isLol ? '装备分类:' : isHsr ? '命途分类:' : isWukong ? '兵刃品阶:' : '武器类型:'}
            </span>
            {availableTypes.map((t) => (
              <button
                key={t}
                onClick={() => setSelectedType(t)}
                className={`px-2.5 py-1 rounded-lg text-xs transition-colors ${
                  selectedType === t
                    ? 'bg-ink-900 text-white font-semibold'
                    : 'bg-canvas text-ink-600 hover:bg-ink-100/80 border border-ink-100/60'
                }`}
              >
                {t === 'ALL' ? '全部' : t}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-ink-500 shrink-0">{isLol || isHok ? '品级档次:' : '稀有度:'}</span>
            {[
              { val: 'ALL', label: '全部' },
              { val: 5, label: isHok ? '★★★★★ 核心大件' : isArknights ? '★★★★★ 顶阶模组' : isZzz ? '★★★★★ S 级音擎' : isLol ? '★★★★★ 成装大件' : '★★★★★ 5星' },
              { val: 4, label: isHok ? '★★★★ 合成中件' : isArknights ? '★★★★ 进阶模组' : isZzz ? '★★★★ A 级音擎' : isLol ? '★★★★ 合成中件' : '★★★★ 4星' },
              ...(isLol || isHok ? [{ val: 3, label: '★★★ 基础小件' }] : []),
            ].map((r) => (
              <button
                key={String(r.val)}
                onClick={() => setSelectedRarity(r.val as number | 'ALL')}
                className={`px-2.5 py-1 rounded-lg text-xs transition-colors ${
                  selectedRarity === r.val
                    ? 'bg-amber-500 text-white font-semibold'
                    : 'text-ink-600 hover:bg-ink-100/70'
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Weapons Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-16 bg-surface rounded-3xl border border-ink-100 p-8 space-y-3">
          <div className="text-4xl">🗡️</div>
          <h3 className="text-base font-bold text-ink-800">{isHok || isLol ? '没有找到匹配的装备' : isArknights ? '没有找到匹配的模组' : isZzz ? '没有找到匹配的音擎' : '没有找到匹配的武器'}</h3>
          <p className="text-xs text-ink-500 max-w-sm mx-auto">
            尝试更换搜索关键词，或清除装备分类与星级筛选条件
          </p>
          <button
            onClick={resetFilters}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-accent-500 text-white shadow-soft hover:bg-accent-600 transition-colors"
          >
            <RotateCcw size={14} /> 清除全部筛选条件
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtered.map((w) => {
            const theme = rarityColorMap[w.rarity] || rarityColorMap[4]
            const rawCurve = w.baseAtkCurve || []
            // 后端多数游戏返回数组；少数返回 {等级: 数值} 对象，这里做兼容归一化
            const curve: { level: string; atk: number | string }[] = Array.isArray(rawCurve)
              ? rawCurve
              : Object.entries(rawCurve as Record<string, number | string>).map(
                  ([k, v]) => ({ level: k, atk: v }),
                )

            const rawRefinements = w.refinements
            const normalizedRefinements: { rank: string; desc: string }[] = Array.isArray(rawRefinements)
              ? rawRefinements
              : typeof rawRefinements === 'object' && rawRefinements !== null
              ? [{
                  rank: rawRefinements.skill_name || '独门妙用 / 专属战技',
                  desc: `${rawRefinements.fp_cost ? `【消耗】${rawRefinements.fp_cost} ` : ''}${rawRefinements.effect || ''}`
                }]
              : []

            const isItem = curve[0]?.level === '合成总价' || w.type?.includes('装备') || w.type?.includes('鞋子')
            const lv1Atk = curve[0]?.atk || '-'
            const lv90Atk = curve[curve.length - 1]?.atk || '-'
            const subStatName = w.subStat?.stat_name || ''
            const subStatLv90 = w.subStat?.values?.[curve[curve.length - 1]?.level || '90'] || w.subStat?.values?.['90'] || '-'
            const sellPrice = curve.find(c => c.level === '出售回收')?.atk ?? '-'

            return (
              <HoverCard
                key={w.id}
                onClick={() => setActiveWeapon(w)}
                className={`p-5 cursor-pointer bg-gradient-to-br ${theme.bg} border border-ink-100/70 hover:shadow-lift transition-all relative overflow-hidden group`}
              >
                <div className="flex items-start gap-4">
                  <div className="h-16 w-16 rounded-2xl bg-surface border-2 border-white shadow-soft p-2 grid place-items-center shrink-0 group-hover:scale-105 transition-transform relative">
                    {w.iconUrl ? (
                      <img
                        src={w.iconUrl}
                        alt={w.name}
                        onError={(e) => {
                          e.currentTarget.style.display = 'none'
                          const fallback = e.currentTarget.nextElementSibling as HTMLElement
                          if (fallback) fallback.style.display = 'grid'
                        }}
                        className="h-full w-full object-contain"
                      />
                    ) : null}
                    <div
                      style={{ display: w.iconUrl ? 'none' : 'grid' }}
                      className="h-full w-full place-items-center text-3xl font-bold text-accent-700"
                    >
                      🗡️
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-base font-bold text-ink-900 group-hover:text-accent-700 transition-colors">{w.name}</h3>
                      <span className="text-amber-500 text-xs tracking-wider">{'★'.repeat(w.rarity)}</span>
                      <Tag size="sm" variant="outline">{w.type}</Tag>
                    </div>
                    
                    {/* Growth specs */}
                    <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                      {isItem ? (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">购买总价 (金币)</span>
                            <span className="font-bold text-amber-700 mt-0.5 block">{curve[0]?.atk ?? '-'} G</span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">出售回收 (金币)</span>
                            <span className="font-bold text-ink-700 mt-0.5 block truncate">
                              {sellPrice} G
                            </span>
                          </div>
                        </>
                      ) : isArknights ? (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">满级攻击加成 (Lv.3)</span>
                            <span className="font-bold text-ink-900 mt-0.5 block">+{lv90Atk} 点</span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">模组分类 / 专属加成</span>
                            <span className="font-bold text-accent-700 mt-0.5 block truncate">
                              {subStatLv90 !== '-' ? subStatLv90 : w.type}
                            </span>
                          </div>
                        </>
                      ) : isZzz ? (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">满级攻击力 (Lv.60)</span>
                            <span className="font-bold text-ink-900 mt-0.5 block">{lv90Atk} 点</span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">高级属性</span>
                            <span className="font-bold text-accent-700 mt-0.5 block truncate">
                              {subStatName ? `${subStatName}: +${subStatLv90 !== '-' ? subStatLv90 : Object.values(w.subStat?.values || {})[0] || '-'}` : w.type}
                            </span>
                          </div>
                        </>
                      ) : isHsr ? (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">满级攻击 (Lv.80)</span>
                            <span className="font-bold text-ink-900 mt-0.5 block">{lv90Atk} 点</span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">专属命途</span>
                            <span className="font-bold text-accent-700 mt-0.5 block truncate">
                              {w.type}命途
                            </span>
                          </div>
                        </>
                      ) : isWukong ? (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">基础攻击力</span>
                            <span className="font-bold text-ink-900 mt-0.5 block">{curve[0]?.atk || '-'} 点</span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">独门妙用/暴击</span>
                            <span className="font-bold text-accent-700 mt-0.5 block truncate">
                              {String(w.subStat?.values?.['暴击率'] || w.subStat?.values?.['独门妙用'] || '神珍专属')}
                            </span>
                          </div>
                        </>
                      ) : isEldenRing ? (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">满级强化攻击</span>
                            <span className="font-bold text-ink-900 mt-0.5 block truncate">
                              {lv90Atk !== '-' ? lv90Atk : lv1Atk}
                            </span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">属性补正 / 必需能力</span>
                            <span className="font-bold text-accent-700 mt-0.5 block truncate">
                              {(w.subStat?.ratings || w.subStat?.requirements) || subStatName || '-'}
                            </span>
                          </div>
                        </>
                      ) : isZelda ? (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">神兵底材基础攻击</span>
                            <span className="font-bold text-ink-900 mt-0.5 block truncate">
                              {lv1Atk}
                            </span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">余料极限 / 特性</span>
                            <span className="font-bold text-accent-700 mt-0.5 block truncate">
                              {lv90Atk !== '-' && lv90Atk !== lv1Atk ? lv90Atk : (w.subStat?.values ? Object.values(w.subStat.values)[0] : '耐久翻倍/绝境增伤')}
                            </span>
                          </div>
                        </>
                      ) : isNaraka ? (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">神兵武备品级 (凡品 ➔ 极品)</span>
                            <span className="font-bold text-ink-900 mt-0.5 block">{lv1Atk} ➔ {lv90Atk} (伤害白值)</span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">招式专属机制</span>
                            <span className="font-bold text-accent-700 mt-0.5 block truncate">
                              {subStatName || '蓄力霸体招式'}
                            </span>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">基础攻击力 (白值)</span>
                            <span className="font-bold text-ink-900 mt-0.5 block">{lv1Atk} ➔ {lv90Atk} (满级)</span>
                          </div>
                          <div className="p-2 rounded-xl bg-surface/80 border border-ink-100/50">
                            <span className="text-ink-400 block text-[10px]">副词条: {subStatName || '无'}</span>
                            <span className="font-bold text-accent-700 mt-0.5 block truncate">
                              {subStatName ? `+${subStatLv90}` : '-'}
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Refinement Skill Teaser */}
                {normalizedRefinements && normalizedRefinements.length > 0 && (
                  <div className="mt-3.5 pt-3 border-t border-ink-100/60 text-xs text-ink-600 line-clamp-2 leading-relaxed">
                    <span className="font-bold text-ink-800 mr-1">
                      {isNaraka
                        ? '独门武学 / 绝招被动:'
                        : isItem
                        ? '装备属性与被动:'
                        : isArknights
                        ? '模组分支特性与天赋升级:'
                        : isZzz
                        ? '音擎专属效果与调律:'
                        : isHsr
                        ? `${normalizedRefinements[0]?.rank || '叠影效果'}:`
                        : isWukong
                        ? '独门妙用:'
                        : isEldenRing
                        ? '专属战技与战灰:'
                        : isZelda
                        ? '神兵觉醒与特效:'
                        : `${normalizedRefinements[0]?.rank || '精炼效果'}:`}
                    </span>
                    {normalizedRefinements[0]?.desc}
                  </div>
                )}

                <div className="mt-3 flex items-center justify-between text-xs font-medium text-accent-700 group-hover:text-accent-800">
                  <span>
                    {isNaraka
                      ? '查看白蓝紫金四阶伤害/独门绝学/开堆出处'
                      : isHok
                      ? '查看售价/唯一被动/合成路径'
                      : isArknights
                      ? '查看模组1~3级数值/特性追加/升级素材'
                      : isZzz
                      ? '查看60级面板/调律1~5阶/改造成材'
                      : isItem
                      ? '查看售价/唯一被动/合成路径'
                      : isHsr
                      ? '查看80级面板/叠影1~5阶/晋阶材料'
                      : isWukong
                      ? '查看独门妙用/神装共鸣/兵刃典故'
                      : isEldenRing
                      ? '查看强化面板/专属战技/补正需求'
                      : isZelda
                      ? '查看余料融合面板/特殊词缀/八爪怪翻新'
                      : '查看全等级/精炼1~5阶/突破材料'}
                  </span>
                  <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                </div>
              </HoverCard>
            )
          })}
        </div>
      )}

      {/* Weapon Detail Modal */}
      <WeaponDetailModal weapon={activeWeapon} onClose={() => setActiveWeapon(null)} />
    </div>
  )
}

// -------------------------------------------------------------
// 3. 圣遗物与符文套装视图 (ArtifactStatsTab)
// -------------------------------------------------------------
export function ArtifactStatsTab({ artifacts }: { artifacts: ArtifactData[] }) {
  const [search, setSearch] = useState('')
  const [selectedRarity, setSelectedRarity] = useState<number | 'ALL'>('ALL')
  const [activeArtifact, setActiveArtifact] = useState<ArtifactData | null>(null)

  const isHokInscription = useMemo(() => {
    return artifacts.some((a) => a.gameId === 24 || a.name?.includes('铭文') || a.rulesReference?.type?.includes('铭文') || a.pieces?.some((p) => p.slot?.includes('铭文')))
  }, [artifacts])

  const isArknightsBranch = useMemo(() => {
    return artifacts.some((a) => a.gameId === 9 || a.name?.includes('分支') || a.rulesReference?.type?.includes('分支') || a.rulesReference?.type?.includes('罗德岛') || a.pieces?.some((p) => p.slot?.includes('费用') || p.slot?.includes('阻挡') || p.slot?.includes('再部署')))
  }, [artifacts])

  const isZzzDisc = useMemo(() => {
    return artifacts.some((a) => a.gameId === 25 || a.name?.includes('重金属') || a.name?.includes('电音') || a.name?.includes('迪斯科') || a.name?.includes('朋克') || a.rulesReference?.type?.includes('驱动盘') || a.pieces?.some((p) => p.slot?.includes('号位')))
  }, [artifacts])

  const isRune = useMemo(() => {
    if (isHokInscription) return false
    return artifacts.some((a) => a.name?.includes('系') || a.pieces?.some((p) => p.slot?.includes('槽位')))
  }, [artifacts, isHokInscription])

  const isRelic = useMemo(() => {
    return artifacts.some((a) => a.rulesReference?.type?.includes('隧洞遗器') || a.rulesReference?.type?.includes('位面饰品') || a.pieces?.some((p) => p.slot?.includes('位面球') || p.slot?.includes('连结绳') || p.slot?.includes('躯干')))
  }, [artifacts])

  const isArmor = useMemo(() => {
    return artifacts.some((a) => a.pieces?.some((p) => p.slot?.includes('头冠') || p.slot?.includes('衣甲') || p.slot?.includes('臂甲') || p.slot?.includes('腿甲')))
  }, [artifacts])

  const isTalisman = useMemo(() => {
    return artifacts.some((a) => a.name?.includes('护符') || a.rulesReference?.type?.includes('护符') || a.twoPieceBonus?.includes('构筑核心'))
  }, [artifacts])

  const isZeldaArmor = useMemo(() => {
    return artifacts.some((a) => a.fourPieceBonus?.includes('大妖精') || a.name?.includes('鬼神') || a.name?.includes('左纳乌') || a.name?.includes('织梦'))
  }, [artifacts])

  const isSouljade = useMemo(() => {
    return artifacts.some((a) => a.gameId === 20 || a.name?.includes('魂玉') || a.rulesReference?.type?.includes('魂玉') || a.twoPieceBonus?.includes('魂玉') || a.twoPieceBonus?.includes('招式质变'))
  }, [artifacts])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return artifacts
      .filter((art) => {
        if (selectedRarity !== 'ALL' && art.rarityMax !== selectedRarity) return false
        if (q) {
          const matchName = art.name?.toLowerCase().includes(q)
          const match2pc = art.twoPieceBonus?.toLowerCase().includes(q)
          const match4pc = art.fourPieceBonus?.toLowerCase().includes(q)
          const matchPiece = art.pieces?.some(p => p.name?.toLowerCase().includes(q) || p.slot?.toLowerCase().includes(q))
          if (!matchName && !match2pc && !match4pc && !matchPiece) return false
        }
        return true
      })
      .sort((a, b) => {
        if (b.rarityMax !== a.rarityMax) return b.rarityMax - a.rarityMax
        return a.name.localeCompare(b.name, 'zh-CN')
      })
  }, [artifacts, search, selectedRarity])

  const isFiltered = search !== '' || selectedRarity !== 'ALL'

  const resetFilters = () => {
    setSearch('')
    setSelectedRarity('ALL')
  }

  return (
    <div className="space-y-6">
      {/* Search & Filter Header */}
      <div className="p-4 rounded-2xl bg-surface border border-ink-100 space-y-3.5 shadow-xs">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={
                isSouljade
                  ? "搜索专属魂玉名称、属性或招式质变效果 (如: 噬魂斩、烈火斩、夺魂、幽冥步)..."
                  : isHokInscription
                  ? "搜索铭文流派、效果或推荐英雄 (如: 无双、夺萃、鹰眼、百穿)..."
                  : isArknightsBranch
                  ? "搜索职业分支特性、干员部署机制 (如: 术战者、解放者、投掷手)..."
                  : isZzzDisc
                  ? "搜索驱动盘套装名称、效果或号位 (如: 极地重金属、啄木鸟电音、冲击力)..."
                  : isRune
                  ? "搜索符文系名称、基石效果或次级联动 (如: 精密、征服者、电刑)..."
                  : isRelic
                  ? "搜索隧洞遗器/位面饰品名称或效果 (如: 铁骑、先驱、都蓝、击破)..."
                  : isArmor
                  ? "搜索披挂防具名称或套装词缀 (如: 大圣、赭黄、定海、识破)..."
                  : isTalisman
                  ? "搜索传奇护符组合或流派机制 (如: 亚历山大、龙徽大盾、鲜血君王)..."
                  : isZeldaArmor
                  ? "搜索防具套装或特质强化 (如: 鬼神、左纳乌、滑翔、潜行)..."
                  : "搜索圣遗物套装名称、效果或部位 (如: 逐影猎人、暴击率、绝缘)..."
              }
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-canvas border border-ink-100 text-ink-900 placeholder:text-ink-400 focus:outline-none focus:border-accent-500 transition-colors"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-ink-400 hover:text-ink-700"
              >
                ✕
              </button>
            )}
          </div>
          <div className="flex items-center gap-2 justify-between sm:justify-end text-xs">
            <span className="text-ink-500 font-medium">
              共 <strong className="text-ink-900 font-bold">{artifacts.length}</strong>{' '}
              {isSouljade ? '枚专属魂玉' : isHokInscription ? '套铭文体系' : isArknightsBranch ? '个职业分支' : isZzzDisc ? '套驱动盘' : isRune ? '套符文体系' : isRelic ? '套遗器与饰品' : isArmor ? '套披挂防具' : isTalisman ? '套传奇护符组合' : isZeldaArmor ? '套防具套装' : '套圣遗物'}，当前展示{' '}
              <strong className="text-accent-600 font-bold">{filtered.length}</strong> {isSouljade ? '枚' : '套'}
            </span>
            {isFiltered && (
              <button
                onClick={resetFilters}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-ink-600 hover:text-ink-900 bg-ink-100/70 hover:bg-ink-200/80 transition-colors font-medium text-[11px]"
              >
                <RotateCcw size={12} /> 重置筛选
              </button>
            )}
          </div>
        </div>

        {/* Rarity filter */}
        <div className="flex items-center gap-2 pt-1 border-t border-ink-100/40 text-xs">
          <span className="font-semibold text-ink-500 shrink-0">
            {isSouljade ? '魂玉品级:' : isHokInscription ? '铭文规格:' : isArknightsBranch ? '分支规格:' : isZzzDisc ? '驱动盘品阶:' : isRune ? '符文规格:' : isRelic ? '遗器品阶:' : isArmor ? '防具品阶:' : isTalisman ? '护符品阶:' : isZeldaArmor ? '防具品质:' : '套装规格:'}
          </span>
          {[
            { val: 'ALL', label: isSouljade ? '全部魂玉' : isHokInscription ? '全部铭文' : isArknightsBranch ? '全部职业分支' : isZzzDisc ? '全部驱动盘' : isRune ? '全部符文系' : isRelic ? '全部遗器饰品' : isArmor ? '全部披挂防具' : isTalisman ? '全部传奇护符' : isZeldaArmor ? '全部防具套装' : '全部套装' },
            { val: 5, label: isSouljade ? '★★★★★ 极品专属魂玉' : isHokInscription ? '★★★★★ 五级铭文套' : isArknightsBranch ? '★★★★★ 六星主力分支' : isZzzDisc ? '★★★★★ S级驱动盘' : isRune ? '★★★★★ 核心基石符文系' : isArmor ? '★★★★★ 神珍防具套装' : isTalisman ? '★★★★★ 传奇护符组' : isZeldaArmor ? '★★★★★ 勇者专属套装' : '★★★★★ 5星金装品阶' },
            { val: 4, label: isSouljade ? '★★★★ 优品专属魂玉' : isHokInscription ? '★★★★ 四级过渡套' : isArknightsBranch ? '★★★★ 进阶职业分支' : isZzzDisc ? '★★★★ A级驱动盘' : isRune ? '★★★★ 次级符文系' : isArmor ? '★★★★ 特品防具套装' : isTalisman ? '★★★★ 高阶护符组' : isZeldaArmor ? '★★★★ 探索实用套装' : '★★★★ 4星紫装品阶' },
          ].map((r) => (
            <button
              key={String(r.val)}
              onClick={() => setSelectedRarity(r.val as number | 'ALL')}
              className={`px-3 py-1 rounded-lg text-xs transition-colors ${
                selectedRarity === r.val
                  ? 'bg-amber-500 text-white font-semibold'
                  : 'bg-canvas text-ink-600 hover:bg-ink-100 border border-ink-100/60'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* Artifacts Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-16 bg-surface rounded-3xl border border-ink-100 p-8 space-y-3">
          <div className="text-4xl">{isSouljade ? '🥋' : '🏺'}</div>
          <h3 className="text-base font-bold text-ink-800">
            {isSouljade ? '没有找到匹配的专属魂玉' : isHokInscription ? '没有找到匹配的铭文体系' : isArknightsBranch ? '没有找到匹配的职业分支' : isZzzDisc ? '没有找到匹配的驱动盘' : isRune ? '没有找到匹配的符文体系' : '没有找到匹配的圣遗物套装'}
          </h3>
          <p className="text-xs text-ink-500 max-w-sm mx-auto">
            尝试更换搜索关键词，或清除筛选条件
          </p>
          <button
            onClick={resetFilters}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-accent-500 text-white shadow-soft hover:bg-accent-600 transition-colors"
          >
            <RotateCcw size={14} /> 清除全部筛选条件
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtered.map((art) => (
            <HoverCard
              key={art.id}
              onClick={() => setActiveArtifact(art)}
              className="p-5 border border-ink-100/70 bg-surface hover:shadow-lift transition-all cursor-pointer relative overflow-hidden group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="h-12 w-12 rounded-xl bg-canvas border border-ink-100 grid place-items-center p-1.5 shrink-0 group-hover:scale-105 transition-transform relative">
                  {art.iconUrl ? (
                    <img
                      src={art.iconUrl}
                      alt={art.name}
                      onError={(e) => {
                        e.currentTarget.style.display = 'none'
                        const fallback = e.currentTarget.nextElementSibling as HTMLElement
                        if (fallback) fallback.style.display = 'grid'
                      }}
                      className="h-full w-full object-contain"
                    />
                  ) : null}
                  <div
                    style={{ display: art.iconUrl ? 'none' : 'grid' }}
                    className="h-full w-full place-items-center text-2xl font-bold text-accent-700"
                  >
                    {isSouljade ? '🥋' : isHokInscription ? '💎' : isZzzDisc ? '💿' : '🏺'}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-base font-bold text-ink-900 group-hover:text-accent-700 transition-colors truncate">
                    {art.name}
                  </h3>
                  <div className="flex items-center gap-1 text-xs text-amber-500">
                    <span>
                      {isSouljade
                        ? (art.rulesReference?.type || '极品专属魂玉 (Souljade)')
                        : isHokInscription
                        ? 'S36 核心铭文定制页 (Inscriptions)'
                        : isArknightsBranch
                        ? (art.rulesReference?.type || '罗德岛职业分支作战体系')
                        : isZzzDisc
                        ? (art.rulesReference?.type || 'S级驱动盘套装 (Drive Disc)')
                        : isRune
                        ? 'S14 核心符文系 (Runes Reforged)'
                        : isRelic
                        ? (art.rulesReference?.type || '5★ 遗器/饰品体系')
                        : isArmor
                        ? (art.rulesReference?.type || '神珍/特品披挂防具')
                        : isTalisman
                        ? (art.rulesReference?.type || '交界地传奇护符组合')
                        : isZeldaArmor
                        ? (art.rulesReference?.type || '海拉鲁防具套装')
                        : `${art.rarityMin}★ ~ ${art.rarityMax}★ 套装`}
                    </span>
                  </div>
                </div>
              </div>

              {/* Set Bonuses */}
              <div className="space-y-2 text-xs">
                <div className="p-3 rounded-xl bg-canvas border border-ink-100">
                  <span className="font-bold text-accent-700 mr-1">
                    {isSouljade ? '【魂玉基础属性与专属机制】' : isHokInscription ? '【红色铭文核心加成】' : isArknightsBranch ? '【职业分支基础特性】' : isZzzDisc ? '【2件套属性】' : isRune ? '【基石核心效果】' : isRelic ? '【2件套属性】' : isArmor ? '【2件套词缀】' : isTalisman ? '【构筑核心机制】' : isZeldaArmor ? '【单件基础效果】' : '【2件套效果】'}
                  </span>
                  <span className="text-ink-700 leading-relaxed line-clamp-2">{art.twoPieceBonus}</span>
                </div>
                <div className="p-3 rounded-xl bg-canvas border border-ink-100">
                  <span className="font-bold text-accent-700 mr-1">
                    {isSouljade ? '【实战招式质变与拼刀收益】' : isHokInscription ? '【绿色+蓝色铭文联动与总属性】' : isArknightsBranch ? '【模组与精二作战机制升华】' : isZzzDisc ? '【4件套机制】' : isRune ? '【次级符文联动】' : isRelic ? '【4件套机制】' : isArmor ? '【4件套神威】' : isTalisman ? '【实战战斗收益】' : isZeldaArmor ? '【二星大妖精套装强化】' : '【4件套效果】'}
                  </span>
                  <span className="text-ink-700 leading-relaxed line-clamp-3">{art.fourPieceBonus}</span>
                </div>
              </div>

              {/* 5 Slots Preview */}
              {art.pieces && art.pieces.length > 0 && (
                <div className="mt-4 pt-3 border-t border-ink-100/60">
                  <div className="text-xs font-semibold text-ink-600 mb-2">
                    {isSouljade ? '专属魂玉规格与流派联动' : isHokInscription ? '3大核心铭文槽位配置' : isArknightsBranch ? '4项部署战术规格' : isZzzDisc ? '驱动盘 1~6 号位规格' : isRune ? '5大核心槽位配置预览' : isRelic ? '部位组件预览' : isArmor ? '4件披挂部位预览' : isTalisman ? '4件核心护符配置预览' : isZeldaArmor ? '套装部位预览' : '5件套部位预览'}
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 text-[11px]">
                    {art.pieces.map((p, i) => (
                      <div key={i} className="p-2 rounded-lg bg-canvas border border-ink-100/80 flex items-center gap-2">
                        {p.icon_url && (
                          <img
                            src={p.icon_url}
                            alt={p.name}
                            onError={(e) => { e.currentTarget.style.display = 'none'; }}
                            className="h-6 w-6 object-contain shrink-0"
                          />
                        )}
                        <span className="font-semibold text-ink-800 truncate">{p.slot} · {p.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-3 flex items-center justify-between text-xs font-medium text-accent-700 group-hover:text-accent-800">
                <span>
                  {isSouljade
                    ? '查看魂玉属性/招式质变倍率/适配神兵'
                    : isHokInscription
                    ? '查看铭文槽位机制与出装搭配'
                    : isArknightsBranch
                    ? '查看职业分支特性与战术部署'
                    : isZzzDisc
                    ? '查看驱动盘主副词条与代理人推荐'
                    : isRune
                    ? '查看符文槽位机制与配置策略'
                    : isRelic
                    ? '查看遗器主词条与词缀强化机制'
                    : isArmor
                    ? '查看披挂部位属性与独门妙用'
                    : isTalisman
                    ? '查看护符四件槽位搭配与收益'
                    : isZeldaArmor
                    ? '查看大妖精强化特质与防御数值'
                    : '查看部位主词条与副词条强化规则'}
                </span>
                <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </div>
            </HoverCard>
          ))}
        </div>
      )}

      {/* Artifact Detail Modal */}
      <ArtifactDetailModal artifact={activeArtifact} onClose={() => setActiveArtifact(null)} />
    </div>
  )
}

// -------------------------------------------------------------
// 4. 底层战斗机制视图 (MechanicRulesTab)
// -------------------------------------------------------------
export function MechanicRulesTab({ mechanics }: { mechanics: MechanicRuleData[] }) {
  return (
    <div className="space-y-4">
      {mechanics.map((m) => (
        <HoverCard key={m.id} className="p-5 border border-ink-100/70 bg-surface">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-accent-100 text-accent-800">
              {m.category}
            </span>
            <h3 className="text-base font-bold text-ink-900">{m.title}</h3>
          </div>

          {/* Formula banner */}
          {m.formula && (
            <div className="my-2.5 p-3 rounded-xl bg-ink-900 text-accent-200 font-mono text-xs overflow-x-auto">
              {m.formula}
            </div>
          )}

          {/* Parameters Detail */}
          {m.parameters && (
            <div className="mt-3 bg-canvas p-3.5 rounded-xl border border-ink-100/60 text-xs space-y-1.5">
              {Object.entries(m.parameters).map(([k, v]) => (
                <div key={k} className="leading-relaxed">
                  <span className="font-semibold text-ink-800">{k}：</span>
                  <span className="text-ink-600 font-mono">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                </div>
              ))}
            </div>
          )}
        </HoverCard>
      ))}
    </div>
  )
}
