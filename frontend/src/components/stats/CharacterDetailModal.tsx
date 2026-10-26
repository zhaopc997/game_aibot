import { useState } from 'react'
import { X, Sparkles, Shield, Swords, Layers, Zap, Award } from 'lucide-react'
import { Tag } from '@/components/ui/Tag'
import type { LevelStat, GameScoped } from './types'

export interface CharacterData extends GameScoped {
  id: number
  name: string
  title?: string
  rarity: number
  element: string
  weaponType: string
  region?: string
  arkhe?: string
  avatarUrl?: string
  splashUrl?: string
  baseStats: LevelStat[]
  specialAscensionStat?: {
    stat_name: string
    stages?: Record<string, string>
    /** 少数游戏用 values 而非 stages 承载同义数据 */
    values?: Record<string, string>
  }
  ascensionMaterials?: {
    tier: string
    items: string
  }[]
  talents?: {
    name: string
    type: string
    description: string
    scaling: Record<string, string>
  }[]
  passives?: {
    name: string
    unlock: string
    desc: string
  }[]
  constellations?: {
    c: number
    name: string
    desc: string
  }[]
  specialMechanics?: Record<string, string>
  recommendations?: {
    weapons?: { bis?: string; alternative_5s?: string; budget_4s?: string }
    artifacts?: { bis_set?: string; alt_set?: string }
    main_stats?: { sands?: string; goblet?: string; circlet?: string }
    sub_stats?: string
  }
}

/** 详情弹窗的 Tab 键（用联合类型替代 any 断言） */
type TabKey = 'levels' | 'talents' | 'constellations' | 'mechanics' | 'builds'

interface Props {
  character: CharacterData | null
  onClose: () => void
}

export function CharacterDetailModal({ character, onClose }: Props) {
  const [activeTab, setActiveTab] = useState<TabKey>('levels')
  const defaultMaxLevel = character?.baseStats?.[character.baseStats.length - 1]?.level || '90'
  const [selectedLevel, setSelectedLevel] = useState<string>(defaultMaxLevel)
  const [avatarErr, setAvatarErr] = useState<boolean>(false)

  if (!character) return null

  const baseStats = character.baseStats || []
  // 显式标注 LevelStat：否则 fallback 字面量会让联合类型缺少可选字段，
  // 后续访问 stamina/mana 等游戏特有字段时编译器不接受。
  const fallbackStat: LevelStat = { level: defaultMaxLevel, hp: '-', atk: '-', def: '-' }
  const currentLevelStat: LevelStat =
    baseStats.find((s) => s.level === selectedLevel) ||
    baseStats[baseStats.length - 1] ||
    fallbackStat

  const elementColorMap: Record<string, { bg: string; text: string; border: string }> = {
    水: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
    火: { bg: 'bg-red-50', text: 'text-red-600', border: 'border-red-200' },
    风: { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-200' },
    雷: { bg: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-200' },
    草: { bg: 'bg-green-50', text: 'text-green-600', border: 'border-green-200' },
    冰: { bg: 'bg-cyan-50', text: 'text-cyan-600', border: 'border-cyan-200' },
    岩: { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200' },
    // 星铁 / 黑神话
    物理: { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200' },
    量子: { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200' },
    虚数: { bg: 'bg-yellow-50', text: 'text-yellow-600', border: 'border-yellow-200' },
    劈棍法: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-300' },
    立棍法: { bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-300' },
    戳棍法: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-300' },
    禁字法: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-300' },
    身外身法: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-300' },
    大圣神威: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-300' },
    // LoL 职业定位
    战士: { bg: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-200' },
    法师: { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200' },
    刺客: { bg: 'bg-rose-50', text: 'text-rose-600', border: 'border-rose-200' },
    射手: { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200' },
    坦克: { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-200' },
    辅助: { bg: 'bg-teal-50', text: 'text-teal-600', border: 'border-teal-200' },
  }

  const isHok = character.gameId === 24 || character.region?.includes('王者大陆') || ['打野', '中路', '发育路', '对抗路', '游走'].includes(character.weaponType)
  const isArknights = character.gameId === 9 || character.region?.includes('罗德岛') || character.element?.includes('近卫') || character.element?.includes('狙击') || character.element?.includes('术师') || character.element?.includes('医疗') || character.baseStats?.[0]?.level?.includes('精0')
  const isZzz = character.gameId === 25 || character.region?.includes('新艾利都') || character.element?.includes('强攻') || character.element?.includes('击破') || character.element?.includes('异常') || character.element?.includes('防护')
  const isLol = !isHok && (['战士', '法师', '刺客', '射手', '坦克', '辅助'].includes(character.element) || Boolean(character.baseStats?.[0]?.spell_block))
  const isHsr = ['毁灭', '巡猎', '智识', '同谐', '虚无', '存护', '丰饶', '记忆', '欢愉'].includes(character.weaponType)
  const isWukong = ['劈棍法', '立棍法', '戳棍法', '禁字法', '身外身法', '大圣神威'].includes(character.element)
  const isEldenRing = ['力信流派', '出血流派', '智力法术', '纯物理纯力', '智敏魔武', '感应龙飨', '全能基准'].includes(character.element) || character.name?.includes('褪色者')
  const isZelda = ['时空突击', '左纳乌工程', '潜行暗杀', '元素魔法', '高空气流', '神圣誓约'].includes(character.element) || character.name?.includes('林克')
  const isNaraka = character.gameId === 20 || character.region?.includes('聚窟洲') || character.region?.includes('昆仑山') || character.region?.includes('无极帝国') || character.region?.includes('日轮国') || character.region?.includes('月轮国') || character.element?.includes('真气') || character.element?.includes('风煞') || character.element?.includes('幻术') || character.element?.includes('佛力') || character.element?.includes('狂战') || character.element?.includes('刺客') || character.element?.includes('控场')

  const elemTheme = elementColorMap[character.element] || (
    isNaraka
      ? character.element?.includes('刺客') || character.element?.includes('幻术')
        ? { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-300' }
        : character.element?.includes('狂战') || character.element?.includes('烈焰')
        ? { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-300' }
        : character.element?.includes('坦克') || character.element?.includes('佛力')
        ? { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-300' }
        : character.element?.includes('辅助') || character.element?.includes('治愈')
        ? { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-300' }
        : { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-300' }
      : { bg: 'bg-accent-50', text: 'text-accent-600', border: 'border-accent-200' }
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-ink-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-4xl max-h-[90vh] bg-surface rounded-3xl shadow-lift border border-ink-100 flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className={`p-6 border-b border-ink-100/60 flex items-start justify-between relative overflow-hidden ${elemTheme.bg}`}>
          <div className="flex items-center gap-4 relative z-10">
            <div className="h-16 w-16 md:h-20 md:w-20 rounded-2xl bg-surface border-2 border-white shadow-soft overflow-hidden shrink-0 grid place-items-center">
              {character.avatarUrl && !avatarErr ? (
                <img 
                  src={character.avatarUrl} 
                  alt={character.name} 
                  onError={() => setAvatarErr(true)}
                  className="h-full w-full object-cover" 
                />
              ) : (
                <div className={`h-full w-full grid place-items-center font-bold text-2xl md:text-3xl ${elemTheme.text} ${elemTheme.bg}`}>
                  {character.name.slice(0, 1)}
                </div>
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-2xl font-bold text-ink-900">{character.name}</h2>
                {character.title && <span className="text-sm text-ink-500 font-normal">· {character.title}</span>}
                <span className="text-amber-500 text-sm tracking-widest">{'★'.repeat(character.rarity)}</span>
              </div>
              <div className="flex items-center gap-2 mt-2 flex-wrap text-xs">
                <span className={`px-2.5 py-0.5 rounded-full font-semibold border ${elemTheme.border} ${elemTheme.text} bg-surface`}>
                  {isNaraka ? `武学流派: ${character.element}` : isHok ? `定位: ${character.element}` : isArknights ? `职阶: ${character.element}` : isZzz ? `特性: ${character.element}` : isLol ? `定位: ${character.element}` : isHsr ? `属性: ${character.element}` : isWukong ? `流派: ${character.element}` : isEldenRing ? `构筑: ${character.element}` : isZelda ? `形态: ${character.element}` : `${character.element}元素`}
                </span>
                <Tag size="sm" variant="outline">{isNaraka ? `擅长神兵: ${character.weaponType}` : isHok ? `分路: ${character.weaponType}` : isArknights ? `分支: ${character.weaponType}` : isZzz ? `武器: ${character.weaponType}` : isHsr ? `命途: ${character.weaponType}` : isWukong ? `兵刃: ${character.weaponType}` : isEldenRing ? `兵刃/触媒: ${character.weaponType}` : isZelda ? `专属武器: ${character.weaponType}` : character.weaponType}</Tag>
                {character.region && <Tag size="sm" variant="outline">{isNaraka ? `势力宗门: ${character.region}` : isHok ? `阵营: ${character.region}` : isArknights ? `势力: ${character.region}` : isZzz ? `阵营: ${character.region}` : isLol ? `城邦: ${character.region}` : character.region}</Tag>}
                {character.arkhe && <Tag size="sm" variant="outline">{isNaraka ? `奥义真气: ${character.arkhe}` : `始基力: ${character.arkhe}`}</Tag>}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full text-ink-500 hover:text-ink-900 hover:bg-white/60 transition-colors z-10"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-ink-100 px-6 gap-2 bg-canvas/60 overflow-x-auto">
          {[
            { key: 'levels', label: isNaraka ? '聚窟洲修行数值' : isArknights ? '精英化成长数值' : isZzz ? '等级与面板成长' : isHok ? '1~15级成长白值' : isZelda ? '心之容器与成长' : isLol ? '1~18级等级成长' : '等级成长数值', icon: <Layers size={14} /> },
            { key: 'talents', label: isNaraka ? '武学绝技 (F技能/V奥义)' : isHok ? '技能全览 (被动/1/2/3技能)' : isArknights ? '核心技能与天赋' : isZzz ? '普攻/特殊技/终结技' : isLol ? '技能全览 (被动/QWER)' : isHsr ? '技能与行迹' : isWukong ? '武学与奇术' : isEldenRing ? '战技与魔法祷告' : isZelda ? '神技与核心战法' : '技能与天赋倍率', icon: <Swords size={14} /> },
            { key: 'constellations', label: isNaraka ? '印记与绝学分支' : isHok ? '关键对局质变期' : isArknights ? '潜能突破 (Potentials)' : isZzz ? '影画配置 (Mindscape)' : isLol ? '关键对局质变期' : isHsr ? '星魂体系 (Eidolons)' : isWukong ? '六根天资觉醒' : isEldenRing ? '大卢恩与护符槽' : isZelda ? '神殿解放与贤者誓约' : '命之座效果', icon: <Award size={14} /> },
            { key: 'mechanics', label: isNaraka ? '拼刀与战斗法则' : isHok ? '王者对战机制' : isArknights ? '泰拉作战机制' : isZzz ? '动作与失衡机制' : isEldenRing ? '交界地战斗机制' : isZelda ? '物理法则与机制' : '底层战斗机制', icon: <Zap size={14} /> },
            { key: 'builds', label: isNaraka ? '推荐神兵与魂玉' : isHok ? '推荐出装与铭文' : isArknights ? '模组与部署建议' : isZzz ? '推荐音擎与驱动盘' : isLol ? '推荐出装与符文' : isHsr ? '推荐光锥与遗器' : isWukong ? '推荐神兵与披挂' : isEldenRing ? '推荐神兵与护符' : isZelda ? '推荐兵刃与防具' : '官方推荐配装', icon: <Sparkles size={14} /> },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as TabKey)}
              className={`inline-flex items-center gap-1.5 py-3 px-3 text-sm font-medium border-b-2 transition-colors shrink-0 ${
                activeTab === tab.key
                  ? 'border-accent-500 text-accent-700 font-semibold'
                  : 'border-transparent text-ink-500 hover:text-ink-700'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {/* Tab: Level Stats */}
          {activeTab === 'levels' && (
            <div className="space-y-6">
              {/* Level Selector Pill Bar */}
              <div>
                <div className="text-xs font-semibold text-ink-500 mb-2 uppercase tracking-wider">选择等级阶段观察面板白字</div>
                <div className="flex flex-wrap gap-1.5">
                  {baseStats.map((st) => (
                    <button
                      key={st.level}
                      onClick={() => setSelectedLevel(st.level)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                        selectedLevel === st.level
                          ? 'bg-accent-500 text-white shadow-soft font-semibold scale-105'
                          : 'bg-ink-100/60 text-ink-700 hover:bg-ink-100'
                      }`}
                    >
                      {st.level.startsWith('精') || st.level.includes('级') ? st.level : `Lv ${st.level}`}
                    </button>
                  ))}
                </div>
              </div>

              {/* Stat Cards for Selected Level */}
              {currentLevelStat && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-4 rounded-2xl bg-canvas border border-ink-100/60">
                    <div className="text-xs text-ink-500">
                      {isNaraka ? '体力上限 (HP)' : isZelda ? '心之容器 (红心)' : isEldenRing ? '生命力 HP' : isArknights ? '生命上限 HP' : '基础生命值'}
                    </div>
                    <div className="text-xl font-bold text-ink-900 mt-1">
                      {isZelda ? (currentLevelStat.hearts || `${currentLevelStat.hp} 点`) : currentLevelStat.hp}
                    </div>
                  </div>
                  <div className="p-4 rounded-2xl bg-canvas border border-ink-100/60">
                    <div className="text-xs text-ink-500">{isNaraka ? '基础攻击系数 (ATK)' : isZelda ? '基础攻击力' : isHok ? '基础物理攻击' : isArknights ? '基础攻击力' : isZzz ? '基础攻击力 (白值)' : isLol ? '基础攻击力' : '基础攻击力 (白字)'}</div>
                    <div className="text-xl font-bold text-ink-900 mt-1">{currentLevelStat.atk}</div>
                  </div>
                  <div className="p-4 rounded-2xl bg-canvas border border-ink-100/60">
                    <div className="text-xs text-ink-500">
                      {isNaraka
                        ? '护甲上限 / 精力上限'
                        : isHok
                        ? '物理防御 / 法术防御'
                        : isArknights
                        ? '物理防御 / 阻挡数'
                        : isZzz
                        ? '基础防御力'
                        : isLol
                        ? '护甲 / 魔抗'
                        : isWukong
                        ? '气力 / 法力上限'
                        : isEldenRing
                        ? '专注 FP / 耐力绿条'
                        : isZelda
                        ? '精力耐力 / 能源电池'
                        : '基础防御力'}
                    </div>
                    <div className="text-xl font-bold text-ink-900 mt-1">
                      {isNaraka
                        ? `${currentLevelStat.armor ?? 1500} / ${currentLevelStat.energy ?? 100} 点`
                        : isHok
                        ? `${currentLevelStat.def} / ${currentLevelStat.spell_block ?? '-'}`
                        : isArknights
                        ? `${currentLevelStat.def} / ${currentLevelStat.block ?? 1}`
                        : isZzz
                        ? currentLevelStat.def
                        : isLol
                        ? `${currentLevelStat.def} / ${currentLevelStat.spell_block ?? '-'}`
                        : isWukong
                        ? `${currentLevelStat.stamina ?? '-'} / ${currentLevelStat.mana ?? '-'}`
                        : isEldenRing
                        ? `${currentLevelStat.fp ?? '-'} / ${currentLevelStat.stamina ?? '-'}`
                        : isZelda
                        ? `${currentLevelStat.stamina ?? '-'} / ${currentLevelStat.battery ?? '-'}`
                        : currentLevelStat.def}
                    </div>
                  </div>
                  <div className="p-4 rounded-2xl bg-canvas border border-ink-100/60">
                    <div className="text-xs text-ink-500">
                      {isNaraka
                        ? '暴击率 / 伤害减免'
                        : isHok
                        ? '暴击率 / 攻速加成'
                        : isArknights
                        ? '法术抗性 / 部署费用'
                        : isZzz
                        ? '冲击力 / 异常精通'
                        : isLol
                        ? '基础攻速 / 暴伤'
                        : isHsr
                        ? '基础行动速度'
                        : isWukong
                        ? '防御 / 暴击率'
                        : isEldenRing
                        ? '强韧度 / 基础防御'
                        : isZelda
                        ? '连击时缓 / 基础防御'
                        : '暴击率 / 暴击伤害'}
                    </div>
                    <div className="text-sm font-bold text-ink-900 mt-1.5">
                      {isNaraka
                        ? `${currentLevelStat.crit_rate || '10.0%'} / 减伤 ${currentLevelStat.def ?? '10%'}`
                        : isHok
                        ? `${currentLevelStat.crit_rate || '0.0%'} / ${currentLevelStat.attack_speed ?? '0%'}`
                        : isArknights
                        ? `${currentLevelStat.res ?? 0} 点 / ${currentLevelStat.cost ?? 19} DP`
                        : isZzz
                        ? `${currentLevelStat.impact ?? 100} 点 / ${currentLevelStat.anomaly_proficiency ?? 88}`
                        : isLol
                        ? `${currentLevelStat.attack_speed ?? '-'} / ${currentLevelStat.crit_dmg || '175.0%'}`
                        : isHsr
                        ? `${currentLevelStat.speed ?? 100} 点`
                        : isWukong
                        ? `${currentLevelStat.def} / ${currentLevelStat.crit_rate ?? '5.0%'}`
                        : isEldenRing
                        ? `${currentLevelStat.poise ?? 0} 点 / 防御 ${currentLevelStat.def}`
                        : isZelda
                        ? `${currentLevelStat.flurry_rush_hits ?? 7} 连击 / 防御 ${currentLevelStat.def}`
                        : `${currentLevelStat.crit_rate || '5.0%'} / ${currentLevelStat.crit_dmg || '50.0%'}`}
                    </div>
                  </div>
                </div>
              )}

              {/* Special Ascension Stat */}
              {character.specialAscensionStat && (
                <div className="p-4 rounded-2xl bg-accent-50/50 border border-accent-100">
                  <h4 className="text-sm font-semibold text-accent-800 flex items-center gap-1.5 mb-2">
                    <Sparkles size={14} className="text-accent-500" />
                    {isNaraka ? '印记神通核心加成：' : isHok ? '核心属性成长机制：' : isArknights ? '精英化天赋增强：' : isZzz ? '核心技额外加成：' : isLol ? '英雄核心成长节点：' : isHsr ? '行迹核心属性加成：' : isWukong ? '流派绝技特权：' : isEldenRing ? '构筑核心特权与机制：' : isZelda ? '专属能力与机制特权：' : '突破专属加成属性：'}
                    {character.specialAscensionStat.stat_name}
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 text-xs">
                    {Object.entries(character.specialAscensionStat.stages || character.specialAscensionStat.values || {}).map(([stage, val]) => (
                      <div key={stage} className="bg-white/80 p-2.5 rounded-xl text-center border border-accent-100/60 shadow-xs">
                        <span className="text-ink-400 block text-[10px] mb-0.5">{stage}</span>
                        <span className="font-bold text-accent-700 block truncate">{String(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Full Level Table */}
              <div>
                <h4 className="text-sm font-semibold text-ink-900 mb-2">
                  {isNaraka ? '聚窟洲各阶段修行白值对照表' : isHok ? '1~15级全阶段基础数值对照表' : isArknights ? '精英化各阶段满级属性对照表' : isZzz ? '1~60级升级与突破面板对照表' : isLol ? '1~18级全阶段数值对照表' : isEldenRing ? '1~150级阶段数值与属性对照表' : isZelda ? '神庙心之容器与探索成长对照表' : '阶段数值对照表'}
                </h4>
                <div className="overflow-x-auto rounded-2xl border border-ink-100 shadow-xs">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-canvas border-b border-ink-100 text-ink-600 font-semibold">
                      {isNaraka ? (
                        <tr>
                          <th className="px-3 py-2.5">修行阶级</th>
                          <th className="px-3 py-2.5">体力上限 (HP)</th>
                          <th className="px-3 py-2.5">攻击系数</th>
                          <th className="px-3 py-2.5">护甲上限</th>
                          <th className="px-3 py-2.5">精力上限</th>
                          <th className="px-3 py-2.5">暴击率 / 减伤</th>
                        </tr>
                      ) : isHok ? (
                        <tr>
                          <th className="px-3 py-2.5">等级</th>
                          <th className="px-3 py-2.5">基础生命</th>
                          <th className="px-3 py-2.5">物理攻击</th>
                          <th className="px-3 py-2.5">物理防御</th>
                          <th className="px-3 py-2.5">法术防御</th>
                          <th className="px-3 py-2.5">暴击 / 攻速</th>
                        </tr>
                      ) : isArknights ? (
                        <tr>
                          <th className="px-3 py-2.5">精英阶段</th>
                          <th className="px-3 py-2.5">生命上限</th>
                          <th className="px-3 py-2.5">基础攻击</th>
                          <th className="px-3 py-2.5">物理防御</th>
                          <th className="px-3 py-2.5">法术抗性</th>
                          <th className="px-3 py-2.5">阻挡 / 部署费用</th>
                        </tr>
                      ) : isZzz ? (
                        <tr>
                          <th className="px-3 py-2.5">等级阶段</th>
                          <th className="px-3 py-2.5">基础生命</th>
                          <th className="px-3 py-2.5">基础攻击力</th>
                          <th className="px-3 py-2.5">基础防御力</th>
                          <th className="px-3 py-2.5">冲击力</th>
                          <th className="px-3 py-2.5">异常精通</th>
                        </tr>
                      ) : isLol ? (
                        <tr>
                          <th className="px-3 py-2.5">等级</th>
                          <th className="px-3 py-2.5">基础生命</th>
                          <th className="px-3 py-2.5">基础攻击力</th>
                          <th className="px-3 py-2.5">基础护甲</th>
                          <th className="px-3 py-2.5">基础魔抗</th>
                          <th className="px-3 py-2.5">基础攻速</th>
                        </tr>
                      ) : isZelda ? (
                        <tr>
                          <th className="px-3 py-2.5">阶段进度</th>
                          <th className="px-3 py-2.5">心之容器</th>
                          <th className="px-3 py-2.5">基础攻击</th>
                          <th className="px-3 py-2.5">精力轮</th>
                          <th className="px-3 py-2.5">能源电池</th>
                          <th className="px-3 py-2.5">基础防御</th>
                        </tr>
                      ) : isEldenRing ? (
                        <tr>
                          <th className="px-3 py-2.5">等级</th>
                          <th className="px-3 py-2.5">生命 HP</th>
                          <th className="px-3 py-2.5">基础攻击</th>
                          <th className="px-3 py-2.5">专注 FP</th>
                          <th className="px-3 py-2.5">精力耐力</th>
                          <th className="px-3 py-2.5">强韧度</th>
                        </tr>
                      ) : (
                        <tr>
                          <th className="px-3 py-2.5">阶段</th>
                          <th className="px-3 py-2.5">基础生命</th>
                          <th className="px-3 py-2.5">基础攻击 (白值)</th>
                          <th className="px-3 py-2.5">基础防御</th>
                          <th className="px-3 py-2.5">暴击率</th>
                          <th className="px-3 py-2.5">暴击伤害</th>
                        </tr>
                      )}
                    </thead>
                    <tbody className="divide-y divide-ink-100/50">
                      {baseStats.map((st: LevelStat) => (
                        <tr 
                          key={st.level} 
                          onClick={() => setSelectedLevel(st.level)}
                          className={`cursor-pointer transition-colors ${selectedLevel === st.level ? 'bg-accent-50/60 font-semibold text-accent-900' : 'hover:bg-canvas/50'}`}
                        >
                          <td className="px-3 py-2 font-mono">{st.level.startsWith('精') || st.level.includes('级') || st.level.includes('(') ? st.level : `Lv ${st.level}`}</td>
                          <td className="px-3 py-2 font-bold text-ink-900">{isZelda ? (st.hearts || st.hp) : st.hp}</td>
                          <td className="px-3 py-2">{st.atk}</td>
                          <td className="px-3 py-2">{isNaraka ? `${st.armor ?? 1500} 点` : isZelda ? (st.stamina || '-') : isEldenRing ? (st.fp || '-') : st.def}</td>
                          {isNaraka ? (
                            <>
                              <td className="px-3 py-2">{st.energy ?? 100} 点</td>
                              <td className="px-3 py-2">{st.crit_rate || '10.0%'} / 减伤 {st.def ?? '10%'}</td>
                            </>
                          ) : isHok ? (
                            <>
                              <td className="px-3 py-2">{st.spell_block ?? '50'}</td>
                              <td className="px-3 py-2">{st.crit_rate || '0.0%'} / {st.attack_speed ?? '0%'}</td>
                            </>
                          ) : isArknights ? (
                            <>
                              <td className="px-3 py-2">{st.res ?? 0} 点</td>
                              <td className="px-3 py-2">阻挡 {st.block ?? 1} / {st.cost ?? 19} DP</td>
                            </>
                          ) : isZzz ? (
                            <>
                              <td className="px-3 py-2">{st.impact ?? 100} 点</td>
                              <td className="px-3 py-2">{st.anomaly_proficiency ?? 88} 点</td>
                            </>
                          ) : isLol ? (
                            <>
                              <td className="px-3 py-2">{st.spell_block ?? '-'}</td>
                              <td className="px-3 py-2">{st.attack_speed ?? '-'}</td>
                            </>
                          ) : isZelda ? (
                            <>
                              <td className="px-3 py-2">{st.battery ?? '-'}</td>
                              <td className="px-3 py-2">{st.def}</td>
                            </>
                          ) : isEldenRing ? (
                            <>
                              <td className="px-3 py-2">{st.stamina ?? '-'}</td>
                              <td className="px-3 py-2">{st.poise ?? '-'}</td>
                            </>
                          ) : (
                            <>
                              <td className="px-3 py-2">{st.crit_rate || '5.0%'}</td>
                              <td className="px-3 py-2">{st.crit_dmg || '50.0%'}</td>
                            </>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Ascension Materials List */}
              {character.ascensionMaterials && character.ascensionMaterials.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-ink-900 mb-2">
                    {isHok ? '关键成长节点' : isArknights ? '精英化进阶与技能升级材料' : isZzz ? '代理人晋升与核心技材料' : isLol ? '对局关键出装节点' : '晋阶突破材料清单'}
                  </h4>
                  <div className="grid sm:grid-cols-2 gap-2 text-xs">
                    {character.ascensionMaterials.map((mat, i) => (
                      <div key={i} className="p-2.5 rounded-xl bg-canvas border border-ink-100 flex items-start gap-2">
                        <span className="font-semibold text-ink-700 shrink-0">{mat.tier}：</span>
                        <span className="text-ink-600">{mat.items}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab: Talents */}
          {activeTab === 'talents' && (
            <div className="space-y-4">
              {character.talents?.map((t, idx) => {
                let badgeText = t.type === 'NORMAL_ATTACK' ? '普通攻击' : t.type === 'ELEMENTAL_SKILL' ? '元素战技 (E)' : t.type === 'ELEMENTAL_BURST' ? '元素爆发 (Q)' : '被动技能'
                if (isNaraka) {
                  if (t.name.includes('(F技能)') || t.name.includes('(F') || t.type === 'ELEMENTAL_SKILL') badgeText = '【F】英雄技能'
                  else if (t.name.includes('(V奥义)') || t.name.includes('(V') || t.type === 'ELEMENTAL_BURST') badgeText = '【V】终极奥义'
                  else badgeText = '【被动】天赋印记'
                } else if (isHok) {
                  if (t.name.startsWith('被动') || t.type === 'PASSIVE') badgeText = '被动技能'
                  else if (t.name.startsWith('一技能')) badgeText = '一技能'
                  else if (t.name.startsWith('二技能')) badgeText = '二技能'
                  else if (t.name.startsWith('三技能') || t.name.startsWith('大招') || t.type === 'ELEMENTAL_BURST') badgeText = '三技能 (大招)'
                } else if (isArknights) {
                  if (t.name.includes('天赋')) badgeText = '特性 / 天赋'
                  else if (t.name.includes('决战') || t.name.includes('三技能')) badgeText = 'S3 决战技能'
                  else if (t.name.includes('二技能')) badgeText = 'S2 核心技能'
                  else if (t.name.includes('一技能')) badgeText = 'S1 技能'
                  else badgeText = '作战技能'
                } else if (isZzz) {
                  if (t.type === 'NORMAL_ATTACK') badgeText = '普通攻击'
                  else if (t.type === 'ELEMENTAL_SKILL' || t.name.includes('特殊技')) badgeText = '特殊技 / 强化特殊技'
                  else if (t.type === 'ELEMENTAL_BURST' || t.name.includes('终结技')) badgeText = '终结技 / 连携技'
                  else if (t.name.includes('闪避')) badgeText = '闪避 / 冲刺反击'
                  else badgeText = '核心被动'
                } else if (isLol) {
                  if (t.name.startsWith('被动技能') || t.type === 'PASSIVE') badgeText = '英雄被动'
                  else if (t.name.startsWith('Q技能')) badgeText = 'Q 技能'
                  else if (t.name.startsWith('W技能')) badgeText = 'W 技能'
                  else if (t.name.startsWith('E技能')) badgeText = 'E 技能'
                  else if (t.name.startsWith('终极技能') || t.type === 'ELEMENTAL_BURST') badgeText = 'R 终极技能'
                }

                return (
                  <div key={idx} className="p-4 rounded-2xl bg-canvas border border-ink-100/80">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-0.5 rounded-md text-xs font-semibold bg-accent-100 text-accent-800">
                        {badgeText}
                      </span>
                      <h4 className="text-base font-bold text-ink-900">{t.name}</h4>
                    </div>
                    <p className="text-xs md:text-sm text-ink-600 mb-3 leading-relaxed">{t.description}</p>
                    {typeof t.scaling === 'string' ? (
                      <div className="bg-surface p-3 rounded-xl border border-ink-100/60 text-xs text-ink-700">
                        <span className="font-semibold text-accent-700">招式倍率：</span> {t.scaling}
                      </div>
                    ) : t.scaling && Object.keys(t.scaling).length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 bg-surface p-3 rounded-xl border border-ink-100/60 text-xs">
                        {Object.entries(t.scaling).map(([k, v]) => (
                          <div key={k} className="flex justify-between py-1 border-b border-ink-100/40 last:border-0">
                            <span className="text-ink-500 font-medium">{k}</span>
                            <span className="font-bold text-ink-800">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                )
              })}

              {/* Passive Talents */}
              {character.passives && character.passives.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-semibold text-ink-900 mb-2">{isNaraka ? '固有武学与被动心法' : isHok ? '局内战斗特性' : isArknights ? '干员专属潜能与天赋机制' : isZzz ? '额外能力与被动机制' : isLol ? '被动机制详解' : '固有天赋机制'}</h4>
                  <div className="space-y-2">
                    {character.passives.map((p, i) => (
                      <div key={i} className="p-3.5 rounded-xl bg-surface border border-ink-100/80 text-xs">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-bold text-ink-900">{p.name}</span>
                          <Tag size="sm" variant="soft">{p.unlock}</Tag>
                        </div>
                        <p className="text-ink-600 leading-relaxed">{p.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab: Constellations */}
          {activeTab === 'constellations' && (
            <div className="space-y-3">
              {character.constellations?.map((c) => (
                <div key={c.c} className="p-4 rounded-2xl bg-canvas border border-ink-100 flex items-start gap-3">
                  <div className="h-8 w-8 rounded-full bg-accent-500 text-white font-bold text-xs grid place-items-center shrink-0 shadow-soft">
                    {isNaraka ? `【${c.c}】` : isHok ? `P${c.c}` : isArknights ? `P${c.c}` : isZzz ? `M${c.c}` : isLol ? `P${c.c}` : isHsr ? `E${c.c}` : isWukong ? `根${c.c}` : `C${c.c}`}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-ink-900 mb-1">
                      {isNaraka
                        ? `绝学分支 ${c.c} · ${c.name}`
                        : isHok
                        ? `期 ${c.c} · ${c.name}`
                        : isArknights
                        ? `潜能 ${c.c} · ${c.name}`
                        : isZzz
                        ? `影画 ${c.c} · ${c.name}`
                        : isLol
                        ? `阶段 ${c.c} · ${c.name}`
                        : isHsr
                        ? `第 ${c.c} 星魂 · ${c.name}`
                        : isWukong
                        ? `${c.name}`
                        : `第 ${c.c} 命 · ${c.name}`}
                    </h4>
                    <p className="text-xs md:text-sm text-ink-600 leading-relaxed">{c.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab: Special Combat Mechanics */}
          {activeTab === 'mechanics' && (
            <div className="space-y-3">
              {character.specialMechanics && Object.entries(character.specialMechanics).map(([k, v]) => (
                <div key={k} className="p-4 rounded-2xl bg-surface border border-ink-100/80 shadow-xs">
                  <div className="text-xs font-bold text-accent-700 uppercase tracking-wider mb-1">{k}</div>
                  <div className="text-sm text-ink-800 leading-relaxed font-mono">{v}</div>
                </div>
              ))}
            </div>
          )}

          {/* Tab: Recommended Builds */}
          {activeTab === 'builds' && character.recommendations && (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-canvas border border-ink-100">
                <h4 className="text-sm font-bold text-ink-900 mb-2 flex items-center gap-1.5">
                  <Swords size={16} className="text-accent-500" /> {isNaraka ? '官方推荐神兵武备 (毕业/副手/过渡)' : isHok ? '局内核心出装' : isArknights ? '专属模组配置 (Modules)' : isZzz ? '推荐音擎 (W-Engines)' : isLol ? '推荐出装路线' : isHsr ? '推荐光锥搭配' : isWukong ? '推荐神珍兵刃' : '推荐武器搭配'}
                </h4>
                <div className="space-y-1.5 text-xs">
                  <div>
                    <span className="font-semibold text-amber-700">{isNaraka ? '毕业神兵：' : isHok ? '核心神装：' : isArknights ? '毕业模组：' : isZzz ? '专属五星音擎：' : isLol ? '核心成装：' : isHsr ? '专属光锥：' : isWukong ? '毕业神兵：' : '毕业专武：'}</span>
                    {character.recommendations.weapons?.bis}
                  </div>
                  <div>
                    <span className="font-semibold text-blue-700">{isNaraka ? '副手备选：' : isHok ? '顺风输出：' : isArknights ? '备选模组：' : isZzz ? '次选音擎：' : isLol ? '次选输出：' : isHsr ? '次选五星光锥：' : isWukong ? '特品备选：' : '次选五星：'}</span>
                    {character.recommendations.weapons?.alternative_5s}
                  </div>
                  <div>
                    <span className="font-semibold text-purple-700">{isNaraka ? '过渡兵刃：' : isHok ? '逆风/保命：' : isArknights ? '基础模组：' : isZzz ? '平民四星音擎：' : isLol ? '保命/过渡：' : isHsr ? '平民四星光锥：' : isWukong ? '前中期过渡：' : '平民四星：'}</span>
                    {character.recommendations.weapons?.budget_4s}
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-canvas border border-ink-100">
                <h4 className="text-sm font-bold text-ink-900 mb-2 flex items-center gap-1.5">
                  <Shield size={16} className="text-accent-500" /> {isNaraka ? '官方推荐专属魂玉搭配 (核心神玉/功能神玉)' : isHok ? '推荐铭文搭配' : isArknights ? '职业分支与编队定位' : isZzz ? '推荐驱动盘套装' : isLol ? '推荐主副系符文' : isHsr ? '推荐隧洞遗器与饰品' : isWukong ? '推荐披挂防具与词缀' : '推荐圣遗物套装'}
                </h4>
                <div className="space-y-1.5 text-xs">
                  <div>
                    <span className="font-semibold text-green-700">{isNaraka ? '核心极品神玉：' : isHok ? '核心铭文套装：' : isArknights ? '战术定位：' : isZzz ? '毕业4件套 / 2件套：' : isLol ? '主系核心符文：' : isHsr ? '毕业4件套 / 2件套：' : isWukong ? '首选披挂防具：' : '首选四件套：'}</span>
                    {character.recommendations.artifacts?.bis_set}
                  </div>
                  <div>
                    <span className="font-semibold text-ink-700">{isNaraka ? '功能与保命魂玉：' : isHok ? '备用铭文方案：' : isArknights ? '编队联动：' : isZzz ? '备选驱动盘组合：' : isLol ? '副系联动符文：' : isHsr ? '备选遗器组合：' : isWukong ? '备选防具搭配：' : '备选过渡：'}</span>
                    {character.recommendations.artifacts?.alt_set}
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-canvas border border-ink-100">
                <h4 className="text-sm font-bold text-ink-900 mb-2 flex items-center gap-1.5">
                  <Layers size={16} className="text-accent-500" /> {isNaraka ? '推荐天赋印记配置 (本源/极阴极阳/万物)' : isHok ? '召唤师技能与加点路线' : isArknights ? '技能专精与站位' : isZzz ? '驱动盘主副词条推荐' : isLol ? '技能加点与召唤师技能' : '圣遗物主副词条推荐'}
                </h4>
                <div className="grid sm:grid-cols-3 gap-2 text-xs mb-3">
                  <div className="p-2.5 rounded-xl bg-surface border border-ink-100">
                    <span className="text-ink-500 block">{isNaraka ? '本源印记 (精力)' : isHok ? '加点顺序' : isArknights ? '专精优先度' : isZzz ? '4号位 (主词条)' : isLol ? '技能加点顺序' : '时之沙 (Sands)'}</span>
                    <span className="font-bold text-ink-900">{character.recommendations.main_stats?.sands}</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-surface border border-ink-100">
                    <span className="text-ink-500 block">{isNaraka ? '极阴印记 (怒气)' : isHok ? '召唤师技能' : isArknights ? '技能回转' : isZzz ? '5号位 (属性伤害)' : isLol ? '召唤师技能' : '空之杯 (Goblet)'}</span>
                    <span className="font-bold text-ink-900">{character.recommendations.main_stats?.goblet}</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-surface border border-ink-100">
                    <span className="text-ink-500 block">{isNaraka ? '万物极阳 (飞索/减伤)' : isHok ? '核心装备' : isArknights ? '攻击范围/朝向' : isZzz ? '6号位 (回能/冲击)' : isLol ? '核心靴子' : '理之冠 (Circlet)'}</span>
                    <span className="font-bold text-ink-900">{character.recommendations.main_stats?.circlet}</span>
                  </div>
                </div>
                <div className="text-xs bg-surface p-2.5 rounded-xl border border-ink-100">
                  <span className="text-ink-500">{isNaraka ? '印记词条优先级：' : isHok ? '局内玩法思路：' : isArknights ? '部署策略建议：' : isZzz ? '副词条优先级：' : isLol ? '符文碎片建议：' : '副词条优先级：'}</span>
                  <span className="font-bold text-ink-800 ml-1">{character.recommendations.sub_stats}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
