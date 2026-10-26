import { useState, useMemo } from 'react'
import { X, Sparkles, Layers, Shield } from 'lucide-react'
import { Tag } from '@/components/ui/Tag'
import { WeaponData } from './GameStatsViews'
import type { RefinementEffect } from './types'

type WeaponTabKey = 'levels' | 'refinements' | 'materials'

interface Props {
  weapon: WeaponData | null
  onClose: () => void
}

export function WeaponDetailModal({ weapon, onClose }: Props) {
  if (!weapon) return null

  const curve: { level: string; atk: number | string }[] = useMemo(() => {
    if (!weapon.baseAtkCurve) return []
    if (Array.isArray(weapon.baseAtkCurve)) return weapon.baseAtkCurve
    {
      // 兼容后端返回 {等级: 数值} 对象的情形
      return Object.entries(weapon.baseAtkCurve as unknown as Record<string, number | string>).map(([k, v]) => ({
        level: k,
        atk: v,
      }))
    }
    return []
  }, [weapon.baseAtkCurve])

  const normalizedRefinements: { rank: string; desc: string }[] = useMemo(() => {
    if (!weapon.refinements) return []
    if (Array.isArray(weapon.refinements)) return weapon.refinements
    if (typeof weapon.refinements === 'object') {
      const r = weapon.refinements as RefinementEffect
      return [{
        rank: r.skill_name || '独门妙用 / 专属战技',
        desc: `${r.fp_cost ? `【消耗/机制】${r.fp_cost}\n` : ''}${r.effect || ''}`
      }]
    }
    return []
  }, [weapon.refinements])

  const normalizedMaterials: { tier?: string; items?: string }[] = useMemo(() => {
    if (!weapon.ascensionMaterials) return []
    if (Array.isArray(weapon.ascensionMaterials)) return weapon.ascensionMaterials
    if (typeof weapon.ascensionMaterials === 'object') {
      const m = weapon.ascensionMaterials
      return [{
        tier: m.type || '获取与强化途径',
        items: m.catalyst_list || ''
      }]
    }
    return []
  }, [weapon.ascensionMaterials])

  const isItem = curve[0]?.level === '合成总价' || weapon.type?.includes('装备') || weapon.type?.includes('鞋子')
  const isModule = weapon.type?.includes('模组')
  const isWEngine = weapon.type?.includes('音擎')
  const isNaraka = Boolean(weapon.gameId === 20 || weapon.type?.includes('近战武器') || weapon.type?.includes('远程武器') || weapon.name?.includes('太刀') || weapon.name?.includes('阔刀') || weapon.name?.includes('斩马刀') || weapon.name?.includes('长枪') || weapon.name?.includes('双节棍') || weapon.name?.includes('鸟铳'))
  const defaultLvl = curve[0]?.level || '90'
  const [activeTab, setActiveTab] = useState<WeaponTabKey>('levels')
  const [selectedLevel, setSelectedLevel] = useState<string>(defaultLvl)
  const [imgErr, setImgErr] = useState<boolean>(false)

  const subStatValues = weapon.subStat?.values || {}
  const subStatName = weapon.subStat?.stat_name || ''
  const subStatRatings = weapon.subStat?.ratings || ''

  const currentStat = curve.find((c) => c.level === selectedLevel) || curve[curve.length - 1] || { level: defaultLvl, atk: 0 }
  const currentSubStat = subStatValues[selectedLevel] || subStatValues[currentStat.level] || '-'

  const rarityColorMap: Record<number, { bg: string; text: string; border: string }> = {
    5: { bg: 'bg-amber-500/10', text: 'text-amber-700', border: 'border-amber-200' },
    4: { bg: 'bg-purple-500/10', text: 'text-purple-700', border: 'border-purple-200' },
    3: { bg: 'bg-blue-500/10', text: 'text-blue-700', border: 'border-blue-200' },
    2: { bg: 'bg-emerald-500/10', text: 'text-emerald-700', border: 'border-emerald-200' },
    1: { bg: 'bg-ink-500/10', text: 'text-ink-700', border: 'border-ink-200' },
  }

  const rTheme = rarityColorMap[weapon.rarity] || rarityColorMap[4]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-ink-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-3xl max-h-[90vh] bg-surface rounded-3xl shadow-lift border border-ink-100 flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className={`p-6 border-b border-ink-100/60 flex items-start justify-between relative overflow-hidden ${rTheme.bg}`}>
          <div className="flex items-center gap-4 relative z-10">
            <div className="h-16 w-16 md:h-20 md:w-20 rounded-2xl bg-surface border-2 border-white shadow-soft overflow-hidden shrink-0 grid place-items-center p-2 relative">
              {weapon.iconUrl && !imgErr ? (
                <img 
                  src={weapon.iconUrl} 
                  alt={weapon.name} 
                  onError={() => setImgErr(true)}
                  className="h-full w-full object-contain" 
                />
              ) : (
                <div className="text-3xl">{isModule ? '📦' : isWEngine ? '📻' : isNaraka ? '⚔️' : '🗡️'}</div>
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-2xl font-bold text-ink-900">{weapon.name}</h2>
                <span className="text-amber-500 text-sm tracking-widest">{'★'.repeat(weapon.rarity)}</span>
              </div>
              <div className="flex items-center gap-2 mt-2 flex-wrap text-xs">
                <Tag size="sm" variant="outline">{weapon.type}</Tag>
                {isItem ? (
                  <span className="px-2.5 py-0.5 rounded-full font-semibold bg-amber-100 text-amber-800">
                    售价: {curve[0]?.atk ?? '-'} G
                  </span>
                ) : isModule ? (
                  <span className="px-2.5 py-0.5 rounded-full font-semibold bg-accent-100 text-accent-800">
                    增益: {subStatName || '专属特性强化'}
                  </span>
                ) : isNaraka ? (
                  <span className="px-2.5 py-0.5 rounded-full font-semibold bg-accent-100 text-accent-800">
                    专属机制: {subStatName || '蓄力霸体招式'}
                  </span>
                ) : subStatName ? (
                  <span className="px-2.5 py-0.5 rounded-full font-semibold bg-accent-100 text-accent-800">
                    {isWEngine ? '高级属性' : '副词条'}: {subStatName}
                  </span>
                ) : null}
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
            { key: 'levels', label: isNaraka ? '神兵品级数值 (凡/良/优/极)' : isModule ? '模组强化阶段' : isItem ? '售价与属性' : '等级成长数值', icon: <Layers size={14} /> },
            { key: 'refinements', label: isNaraka ? '独门武学与霸体绝招' : isModule ? '特性与天赋强化' : isWEngine ? '音擎效果 (1~5星)' : isItem ? '装备属性与唯一被动' : '1~5阶精炼效果', icon: <Sparkles size={14} /> },
            { key: 'materials', label: isNaraka ? '空投与金堆锻造出处' : isModule ? '解锁与升级材料' : isWEngine ? '晋阶突破材料' : isItem ? '合成路径与配方' : '突破材料清单', icon: <Shield size={14} /> },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as WeaponTabKey)}
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
              {isItem ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-canvas border border-ink-100/80 text-center">
                      <div className="text-xs text-ink-500 mb-1">购买总价 (金币)</div>
                      <div className="text-3xl font-display font-bold text-amber-700">{curve[0]?.atk ?? '-'} G</div>
                    </div>
                    <div className="p-4 rounded-2xl bg-canvas border border-ink-100/80 text-center">
                      <div className="text-xs text-ink-500 mb-1">出售回收 (金币)</div>
                      <div className="text-3xl font-display font-bold text-ink-700">
                        {curve.find(c => c.level === '出售回收')?.atk ?? '-'} G
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-ink-900 mb-2">装备主属性与买卖价格明细</h4>
                    <div className="overflow-x-auto rounded-2xl border border-ink-100 shadow-xs">
                      <table className="w-full text-xs text-left">
                        <thead className="bg-canvas border-b border-ink-100 text-ink-600 font-semibold">
                          <tr>
                            <th className="px-3 py-2.5">买卖项目</th>
                            <th className="px-3 py-2.5">金额</th>
                            <th className="px-3 py-2.5">说明</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-ink-100/50">
                          {curve.map((st) => (
                            <tr key={st.level} className="hover:bg-canvas/50">
                              <td className="px-3 py-2.5 font-bold text-ink-900">{st.level}</td>
                              <td className="px-3 py-2.5 font-mono text-amber-700 font-bold">{st.atk} 金币</td>
                              <td className="px-3 py-2.5 text-ink-600">
                                {st.level === '合成总价' ? '商店购买或合成所需的全部金币' : '卖回商店时可回收的金币'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  {/* Level Selector */}
                  <div>
                    <div className="text-xs font-semibold text-ink-500 mb-2 uppercase tracking-wider">{isNaraka ? '选择神兵品级查看伤害白值与招式机制' : '选择等级阶段观察面板数值'}</div>
                    <div className="flex flex-wrap gap-1.5">
                      {curve.map((st) => (
                        <button
                          key={st.level}
                          onClick={() => setSelectedLevel(st.level)}
                          className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                            selectedLevel === st.level
                              ? 'bg-accent-500 text-white shadow-soft font-semibold scale-105'
                              : 'bg-ink-100/60 text-ink-700 hover:bg-ink-100'
                          }`}
                        >
                          {st.level.startsWith('Lv') || st.level.startsWith('精') || st.level.includes('武') || st.level.includes('品') || st.level.includes('级') ? st.level : `Lv ${st.level}`}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Current Level Stat Cards */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-canvas border border-ink-100/80 text-center">
                      <div className="text-xs text-ink-500 mb-1">{isNaraka ? `${selectedLevel} 伤害数值` : isModule ? `${selectedLevel} 强化效果` : isWEngine ? `${selectedLevel} 基础攻击力` : `${selectedLevel} 基础攻击力 (面板)`}</div>
                      <div className="text-xl sm:text-2xl font-display font-bold text-ink-900 truncate">{String(currentStat.atk || '-')}</div>
                    </div>
                    <div className="p-4 rounded-2xl bg-canvas border border-ink-100/80 text-center">
                      <div className="text-xs text-ink-500 mb-1">{isNaraka ? '招式专属机制' : isModule ? '干员属性加成' : isWEngine ? '高级属性' : (subStatName || '副词条/补正')}</div>
                      <div className="text-sm font-bold text-accent-700 mt-2 truncate">
                        {subStatRatings ? subStatRatings : (subStatName ? (isModule || isNaraka ? currentSubStat : `+${currentSubStat}`) : '专属机制')}
                      </div>
                    </div>
                  </div>

                  {/* Full Level Table */}
                  <div>
                    <h4 className="text-sm font-semibold text-ink-900 mb-2">{isNaraka ? '白蓝紫金四品伤害与机制明细' : isModule ? '模组各阶段强化与增益明细' : '阶段面板数值对照表'}</h4>
                    <div className="overflow-x-auto rounded-2xl border border-ink-100 shadow-xs">
                      <table className="w-full text-xs text-left">
                        <thead className="bg-canvas border-b border-ink-100 text-ink-600 font-semibold">
                          <tr>
                            <th className="px-3 py-2.5">{isNaraka ? '神兵武备品阶' : '阶段等级'}</th>
                            <th className="px-3 py-2.5">{isNaraka ? '攻击伤害数值' : isModule ? '模组强化效果' : '基础攻击力 (面板)'}</th>
                            {subStatName && <th className="px-3 py-2.5">{isNaraka ? `招式机制: ${subStatName}` : isModule ? '干员属性增益' : isWEngine ? `高级属性: ${subStatName}` : `副词条: ${subStatName}`}</th>}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-ink-100/50">
                          {curve.map((st) => (
                            <tr 
                              key={st.level} 
                              onClick={() => setSelectedLevel(st.level)}
                              className={`cursor-pointer transition-colors ${selectedLevel === st.level ? 'bg-accent-50/60 font-semibold text-accent-900' : 'hover:bg-canvas/50'}`}
                            >
                              <td className="px-3 py-2 font-mono">{st.level}</td>
                              <td className="px-3 py-2 font-bold">{String(st.atk)}</td>
                              {subStatName && (
                                <td className="px-3 py-2 text-accent-700">
                                  {subStatValues[st.level] ? (isModule ? subStatValues[st.level] : `+${subStatValues[st.level]}`) : '-'}
                                </td>
                              )}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Tab: Refinements */}
          {activeTab === 'refinements' && (
            <div className="space-y-3">
              {normalizedRefinements.length > 0 ? (
                normalizedRefinements.map((r, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-canvas border border-ink-100">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className={`px-2.5 py-0.5 rounded-lg text-xs font-bold ${
                        isItem 
                          ? 'bg-accent-500 text-white' 
                          : idx === 4 ? 'bg-amber-500 text-white' : idx === 0 ? 'bg-accent-500 text-white' : 'bg-ink-200 text-ink-800'
                      }`}>
                        {isItem ? '装备属性与唯一被动' : `${r.rank} ${idx === 4 ? '(满精)' : ''}`}
                      </span>
                    </div>
                    <p className="text-xs md:text-sm text-ink-700 leading-relaxed whitespace-pre-line">{r.desc}</p>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-ink-400 text-xs">该装备无特殊技能或被动效果</div>
              )}
            </div>
          )}

          {/* Tab: Materials */}
          {activeTab === 'materials' && (
            <div className="space-y-3">
              {normalizedMaterials.length > 0 ? (
                <div className="space-y-2">
                  {normalizedMaterials.map((mat, i) => (
                    <div key={i} className="p-3.5 rounded-xl bg-canvas border border-ink-100 flex items-start gap-3 text-xs">
                      <span className="font-bold text-accent-700 shrink-0">{mat.tier}：</span>
                      <span className="text-ink-700 leading-relaxed">{mat.items}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-10 text-ink-400 text-xs">暂无合成材料明细</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
