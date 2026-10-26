import { useState } from 'react'
import { X, Gem, Shield, Layers } from 'lucide-react'
import { Tag } from '@/components/ui/Tag'
import { ArtifactData } from './GameStatsViews'

interface Props {
  artifact: ArtifactData | null
  onClose: () => void
}

export function ArtifactDetailModal({ artifact, onClose }: Props) {
  const [imgErr, setImgErr] = useState<boolean>(false)

  if (!artifact) return null

  const isSouljade = Boolean(artifact.gameId === 20 || artifact.name?.includes('魂玉') || artifact.rulesReference?.type?.includes('魂玉') || artifact.pieces?.[0]?.slot?.includes('魂玉') || artifact.twoPieceBonus?.includes('魂玉') || artifact.twoPieceBonus?.includes('招式质变'))
  const isHokInscription = !isSouljade && Boolean(artifact.name?.includes('铭文') || artifact.name?.includes('穿') || artifact.pieces?.[0]?.slot?.includes('色铭文'))
  const isArknightsBranch = !isSouljade && Boolean(artifact.name?.includes('分支') || artifact.name?.includes('职阶') || artifact.pieces?.[0]?.slot?.includes('分支'))
  const isZzzDisc = !isSouljade && Boolean(artifact.name?.includes('电音') || artifact.name?.includes('重金属') || artifact.name?.includes('爵士') || artifact.name?.includes('朋克') || artifact.name?.includes('迪斯科') || artifact.name?.includes('蓝调') || artifact.pieces?.[0]?.slot?.includes('号位'))
  const isRune = !isSouljade && !isHokInscription && Boolean(artifact.rulesReference?.primary_tree || artifact.pieces?.[0]?.slot?.includes('槽位'))
  const isTalisman = !isSouljade && Boolean(artifact.name?.includes('护符') || artifact.pieces?.[0]?.slot?.includes('护符') || artifact.rulesReference?.type?.includes('护符'))
  const isArmor = !isSouljade && Boolean(artifact.name?.includes('套装') || artifact.pieces?.[0]?.slot?.includes('头部') || artifact.pieces?.[0]?.slot?.includes('胸甲') || artifact.pieces?.[0]?.slot?.includes('头冠'))
  const hasSubStatTiers = Boolean(artifact.rulesReference?.sub_stat_tiers_4star_and_5star)

  const subStatTiers = artifact.rulesReference?.sub_stat_tiers_4star_and_5star || {
    crit_rate: ['2.7%', '3.1%', '3.5%', '3.9%'],
    crit_dmg: ['5.4%', '6.2%', '7.0%', '7.8%'],
    atk_percent: ['4.1%', '4.7%', '5.3%', '5.8%'],
    energy_recharge: ['4.5%', '5.2%', '5.8%', '6.5%'],
    elemental_mastery: [16, 19, 21, 23],
    hp_percent: ['4.1%', '4.7%', '5.3%', '5.8%'],
    def_percent: ['5.1%', '5.8%', '6.6%', '7.3%']
  }

  const statLabels: Record<string, string> = {
    crit_rate: '暴击率 (Crit Rate)',
    crit_dmg: '暴击伤害 (Crit DMG)',
    atk_percent: '攻击力百分比 (ATK%)',
    energy_recharge: '元素充能效率 (ER%)',
    elemental_mastery: '元素精通 (EM)',
    hp_percent: '生命值百分比 (HP%)',
    def_percent: '防御力百分比 (DEF%)'
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-ink-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-3xl max-h-[90vh] bg-surface rounded-3xl shadow-lift border border-ink-100 flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-ink-100/60 flex items-start justify-between relative overflow-hidden bg-gradient-to-br from-amber-500/10 to-canvas">
          <div className="flex items-center gap-4 relative z-10">
            <div className="h-16 w-16 md:h-20 md:w-20 rounded-2xl bg-surface border-2 border-white shadow-soft overflow-hidden shrink-0 grid place-items-center p-2 relative">
              {artifact.iconUrl && !imgErr ? (
                <img 
                  src={artifact.iconUrl} 
                  alt={artifact.name} 
                  onError={() => setImgErr(true)}
                  className="h-full w-full object-contain" 
                />
              ) : (
                <div className="text-3xl">{isSouljade ? '🥋' : isHokInscription ? '💎' : isArknightsBranch ? '🎖️' : isZzzDisc ? '💿' : isRune ? '⚡' : isTalisman ? '🧿' : isArmor ? '🛡️' : '🏺'}</div>
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-2xl font-bold text-ink-900">{artifact.name}</h2>
                <span className="text-amber-500 text-sm font-semibold">
                  {isSouljade
                    ? '极品专属魂玉 (Souljade)'
                    : isHokInscription
                    ? '5级通用铭文方案 (Inscriptions)'
                    : isArknightsBranch
                    ? '干员职业子分支特性 (Archetype)'
                    : isZzzDisc
                    ? 'S级/A级驱动盘套装 (Drive Discs)'
                    : isRune
                    ? 'S14 核心符文系 (Runes Reforged)'
                    : `${artifact.rarityMin}★ ~ ${artifact.rarityMax}★ 套装`}
                </span>
              </div>
              <p className="text-xs text-ink-500 mt-1">
                {isSouljade
                  ? (artifact.rulesReference?.recommended_for ? `适配神兵/英雄: ${artifact.rulesReference.recommended_for}` : '聚窟洲极品专属魂玉，镶嵌后大幅强化招式机制与面板属性')
                  : isHokInscription
                  ? (artifact.rulesReference?.recommended_for ? `推荐英雄: ${artifact.rulesReference.recommended_for}` : '包含红色攻击/穿透、绿色穿透/冷却、蓝色移速/吸血等10个铭文槽位组合')
                  : isArknightsBranch
                  ? (artifact.rulesReference?.recommended_for ? `代表干员: ${artifact.rulesReference.recommended_for}` : '包含子职业攻击范围、阻挡机制与战术部署规则')
                  : isZzzDisc
                  ? (artifact.rulesReference?.recommended_for ? `首选代理人: ${artifact.rulesReference.recommended_for}` : '包含 I ~ VI 号位 6 大驱动盘槽位及主副词条规格')
                  : isRune
                  ? (artifact.rulesReference?.recommended_for ? `推荐英雄: ${artifact.rulesReference.recommended_for}` : '包含基石槽位、次级符文联动与属性碎片')
                  : isTalisman
                  ? (artifact.rulesReference?.recommended_for ? `适用流派: ${artifact.rulesReference.recommended_for}` : '包含核心传奇护符搭配组合')
                  : isArmor
                  ? (artifact.rulesReference?.recommended_for ? `推荐搭配: ${artifact.rulesReference.recommended_for}` : '包含头盔、胸甲、臂甲、腿甲等核心防具部件')
                  : '包含生之花、死之羽、时之沙、空之杯、理之冠 5 大部位'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full text-ink-500 hover:text-ink-900 hover:bg-white/60 transition-colors z-10"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {/* Set Bonuses */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-ink-900 flex items-center gap-1.5">
              <Gem size={15} className="text-accent-500" /> {isSouljade ? '专属魂玉加成效果与招式质变' : isHokInscription ? '铭文方案满配加成属性' : isArknightsBranch ? '职业分支特性与战术效果' : isZzzDisc ? '驱动盘套装效果 (2件套 / 4件套)' : isRune ? '符文机制与联动收益' : '套装技能与机制加成'}
            </h4>
            <div className="p-4 rounded-2xl bg-canvas border border-ink-100 space-y-1">
              <div className="text-xs font-bold text-accent-700">{isSouljade ? '【魂玉基础属性与专属机制】' : isHokInscription ? '【核心面板属性加成】' : isArknightsBranch ? '【子职业核心战斗特性】' : isZzzDisc ? '【2件套基础效果】' : isRune ? '【基石符文核心机制】' : '【2件套效果】'}</div>
              <p className="text-xs md:text-sm text-ink-800 leading-relaxed">{artifact.twoPieceBonus}</p>
            </div>
            <div className="p-4 rounded-2xl bg-canvas border border-ink-100 space-y-1">
              <div className="text-xs font-bold text-accent-700">{isSouljade ? '【实战招式质变与拼刀收益】' : isHokInscription ? '【复合功能收益与移速】' : isArknightsBranch ? '【战场部署战略定位】' : isZzzDisc ? '【4件套核心被动机制】' : isRune ? '【次级符文体系联动】' : '【4件套效果】'}</div>
              <p className="text-xs md:text-sm text-ink-800 leading-relaxed">{artifact.fourPieceBonus}</p>
            </div>
          </div>

          {/* Pieces Details */}
          {artifact.pieces && artifact.pieces.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-ink-900 mb-3 flex items-center gap-1.5">
                <Shield size={15} className="text-accent-500" /> {isSouljade ? '专属魂玉规格与流派联动' : isHokInscription ? '红绿蓝三色铭文槽位配置' : isArknightsBranch ? '分支机制特性与攻击范围' : isZzzDisc ? '1 ~ 6 号位驱动盘槽位规格' : isRune ? '五大符文配置槽位与核心效果' : '套装部位与主词条规格'}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {artifact.pieces.map((p, idx) => (
                  <div key={idx} className="p-3.5 rounded-2xl bg-surface border border-ink-100 flex items-center gap-3">
                    <div className="h-12 w-12 rounded-xl bg-canvas border border-ink-100 grid place-items-center p-1.5 shrink-0">
                      {p.icon_url ? (
                        <img
                          src={p.icon_url}
                          alt={p.name}
                          onError={(e) => { e.currentTarget.style.display = 'none'; }}
                          className="h-full w-full object-contain"
                        />
                      ) : null}
                      <span className="text-xl">{isSouljade ? '📿' : '✨'}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <Tag size="sm" variant="soft">{p.slot}</Tag>
                        <span className="font-bold text-ink-900 text-xs truncate">{p.name}</span>
                      </div>
                      <div className="text-[11px] text-ink-500 mt-1 line-clamp-2">
                        {p.main_stat_rule}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sub-stat Roll Reference, Rune Strategies, or Build Recommendations */}
          {isRune ? (
            <div className="p-4 rounded-2xl bg-canvas border border-ink-100 space-y-2.5">
              <h4 className="text-sm font-bold text-ink-900 flex items-center gap-1.5">
                <Layers size={15} className="text-accent-500" /> 符文重铸 (Runes Reforged) 搭配策略
              </h4>
              <p className="text-xs text-ink-700 leading-relaxed">
                1. <strong>基石符文决定对局输出风格</strong>：例如致命节奏/征服者主打持续普攻与自适应吸血；电刑/黑暗收割主打极致爆发与残血收割；奥术彗星主打远程对线耗血与压制。
              </p>
              <p className="text-xs text-ink-700 leading-relaxed">
                2. <strong>次级槽位弥补英雄短板</strong>：提供击杀即时回复（凯旋）、续航法力（法力流系带）、技能急速冷却缩减（超然）或残血逆境反杀（坚毅不倒/致命一击）。
              </p>
              <p className="text-xs text-ink-700 leading-relaxed">
                3. <strong>副系选择与属性碎片</strong>：根据对局对线压力灵活选择副系（如启迪系神奇之鞋/饼干配送稳线，或坚决系复苏之风抗压）。
              </p>
            </div>
          ) : hasSubStatTiers ? (
            <div>
              <h4 className="text-sm font-bold text-ink-900 mb-2 flex items-center gap-1.5">
                <Layers size={15} className="text-accent-500" /> 5星圣遗物副词条 4 档强化数值库
              </h4>
              <div className="overflow-x-auto rounded-2xl border border-ink-100 shadow-xs">
                <table className="w-full text-xs text-left">
                  <thead className="bg-canvas border-b border-ink-100 text-ink-600 font-semibold">
                    <tr>
                      <th className="px-3 py-2">副词条属性</th>
                      <th className="px-3 py-2">第 1 档 (最低)</th>
                      <th className="px-3 py-2">第 2 档</th>
                      <th className="px-3 py-2">第 3 档</th>
                      <th className="px-3 py-2">第 4 档 (满档)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-ink-100/50">
                    {Object.entries(subStatTiers).map(([k, tiers]) => (
                      <tr key={k} className="hover:bg-canvas/40">
                        <td className="px-3 py-2 font-medium text-ink-800">{statLabels[k] || k}</td>
                        <td className="px-3 py-2 text-ink-600">{tiers[0]}</td>
                        <td className="px-3 py-2 text-ink-600">{tiers[1]}</td>
                        <td className="px-3 py-2 text-ink-600">{tiers[2]}</td>
                        <td className="px-3 py-2 font-bold text-accent-700">{tiers[3]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-canvas border border-ink-100 space-y-2">
              <h4 className="text-sm font-bold text-ink-900 flex items-center gap-1.5">
                <Layers size={15} className="text-accent-500" /> {isSouljade ? '专属魂玉实战心得与连招推荐' : isHokInscription ? '铭文搭配实战建议' : isArknightsBranch ? '职业分支战场定位' : isZzzDisc ? '驱动盘搭配与属性适配' : '构筑类型与实战搭配推荐'}
              </h4>
              <div className="text-xs text-ink-700 space-y-1.5">
                {artifact.rulesReference?.type && (
                  <div>
                    <strong className="text-ink-900">{isSouljade ? '魂玉分类：' : isHokInscription ? '铭文类型：' : isArknightsBranch ? '职阶分类：' : isZzzDisc ? '套装定位：' : '构筑定位：'}</strong> {artifact.rulesReference.type}
                  </div>
                )}
                {artifact.rulesReference?.recommended_for && (
                  <div>
                    <strong className="text-accent-700">{isSouljade ? '适配神兵/英雄：' : isHokInscription ? '首选英雄：' : isArknightsBranch ? '代表干员：' : isZzzDisc ? '首选代理人：' : '推荐适配：'}</strong> {artifact.rulesReference.recommended_for}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
