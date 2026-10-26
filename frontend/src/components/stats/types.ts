/**
 * 数值组件的共享类型。
 *
 * 背景：本项目各游戏的数值字段差异很大（原神是 hp/atk/def，明日方舟是
 * block/res/cost，黑神话是 stamina/mana，塞尔达是 hearts/stamina…），
 * 后端返回的 baseStats 是同一张表里混装这些字段。
 *
 * 此前这些"非通用字段"没有在类型里声明，代码只能写 `(stat as any).block`
 * 来绕过类型检查。集中声明为可选字段后即可去掉全部 any 断言，
 * 同时保留"字段可能存在也可能不存在"的真实语义。
 */

/** 单个等级的数值行：通用字段必填，游戏特有字段可选 */
export interface LevelStat {
  level: string
  hp: number | string
  atk: number | string
  def: number | string

  // ───── 通用可选 ─────
  crit_rate?: string
  crit_dmg?: string

  // ───── 游戏特有（按游戏出现）─────
  /** 明日方舟：法术抗性 */
  res?: number | string
  /** 明日方舟：阻挡数 */
  block?: number | string
  /** 明日方舟：部署费用 */
  cost?: number | string
  /** 原神/通用：元素护盾或格挡值 */
  spell_block?: number | string
  /** 攻击速度（百分比字符串，如 "12%"） */
  attack_speed?: string
  /** 移动/出手速度点数 */
  speed?: number | string
  /** 体力（塞尔达/黑神话等） */
  stamina?: number | string
  /** 法力（黑神话等） */
  mana?: number | string
  /** 专注点（黑神话） */
  fp?: number | string
  /** 生命上限（塞尔达） */
  hearts?: number | string
  /** 能量/电量 */
  battery?: number | string
  /** 失衡值/冲击力 */
  impact?: number | string
  /** 异常精通 */
  anomaly_proficiency?: number | string
  /** 韧性 */
  poise?: number | string
  /** 连击段数 */
  flurry_rush_hits?: number | string
  /** 永劫无间：护甲值/护甲上限 */
  armor?: number | string
  /** 永劫无间：精力上限/精力恢复 */
  energy?: number | string
}

/** 武器精炼/强化效果 */
export interface RefinementEffect {
  /** 效果描述 */
  effect?: string
  /** 消耗（如黑神话的 fp_cost） */
  fp_cost?: number | string  /** 技能名 */
  skill_name?: string
}

/** 带游戏归属的实体（用于按 gameId 区分展示逻辑） */
export interface GameScoped {
  /** 所属游戏 id。后端部分接口未返回，故为可选 */
  gameId?: number
}
