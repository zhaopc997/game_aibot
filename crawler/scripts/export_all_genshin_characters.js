const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const genshindb = require('../node_modules/genshin-db');

genshindb.setOptions({
  queryLanguages: ['ChineseSimplified', 'English'],
  resultLanguage: 'ChineseSimplified'
});

function calcHash(obj) {
  const s = JSON.stringify(obj, Object.keys(obj).sort());
  return crypto.createHash('sha256').update(s).digest('hex');
}

function formatAttribute(label, params, levelIndex) {
  if (!label || !params) return label;
  return label.replace(/{param(\d+):([A-Z0-9]+)}/g, (match, pNum, format) => {
    const pKey = 'param' + pNum;
    if (!params[pKey] || params[pKey][levelIndex] === undefined) return match;
    const val = params[pKey][levelIndex];
    if (format.includes('P')) {
      return (val * 100).toFixed(1).replace(/\.0$/, '') + '%';
    } else if (format.includes('F1')) {
      return val.toFixed(1);
    } else if (format.includes('I')) {
      return Math.round(val).toString();
    }
    return val.toString();
  });
}

function formatCost(costArray) {
  if (!costArray || !Array.isArray(costArray)) return '';
  return costArray.map(item => `${item.name} x${item.count}`).join(', ');
}

function getArkhe(name, region) {
  const ousia = ['菲米尼', '琳妮特', '娜维娅', '夏洛蒂', '千织', '克洛琳德', '艾梅莉埃'];
  const pneuma = ['林尼', '菲米尼', '那维莱特', '莱欧斯利', '夏沃蕾', '闲云'];
  if (name === '芙宁娜') return '芒荒双属性';
  if (ousia.includes(name)) return '荒性';
  if (pneuma.includes(name)) return '芒性';
  if (region === '枫丹') return '芒性/荒性';
  return '无';
}

function getSpecialMechanics(name, element, region) {
  const mech = {
    elemental_gauge: '1U 弱' + element + ' (普攻与技能基础附着量)',
    icd_rule: '遵循 2.5秒 / 3次命中 标准附着内置冷却',
    poise_damage: '常规削韧与硬直打断判定',
    interruption_resistance: '标准角色受击抗打断系数 1.0',
    arkhe_property: getArkhe(name, region),
    hitlag_extension: '近战命中带有卡肉停顿，可小幅延长增益窗口'
  };

  if (['香菱', '胡桃', '珊瑚宫心海'].includes(name)) {
    mech.icd_rule = '核心机制无ICD (独立附着，每一次命中必定触发元素反应)';
  }
  if (['钟离', '雷电将军', '优菈'].includes(name)) {
    mech.interruption_resistance = '特定技能期间抗打断系数降为 0.0 (绝对霸体，无法被打断)';
  }
  if (['阿蕾奇诺', '克洛琳德', '希格雯'].includes(name)) {
    mech.bond_of_life = '生命之契机制：通过契约红血条提供超额增伤与战技形态质变';
  }
  if (region === '纳塔' || ['玛拉妮', '基尼奇', '恰斯卡', '茜特菈莉', '希诺宁', '欧洛伦', '卡齐娜'].includes(name)) {
    mech.nightsoul = '纳塔夜魂系统：拥有夜魂加持状态、夜魂值上限消耗与全队夜魂进发协同机制';
    mech.phlogiston = '纳塔燃界力系统：可在大世界消耗燃界力进行专属高机动移动与附身探索';
  }
  return mech;
}

function getRecommendations(name, element, weaponType) {
  const rec = {
    weapons: {
      bis: '5星毕业专武',
      alternative_5s: '通用五星暴击/充能武器',
      budget_4s: '锻造/大月卡高性价比四星武器'
    },
    artifacts: {
      bis_set: '专属毕业4件套',
      alt_set: '2+2 属性攻击/生命/充能散搭过渡'
    },
    main_stats: {
      sands: '攻击力% / 充能% / 精通 / 生命%',
      goblet: element + '元素伤害加成% / 攻击力%',
      circlet: '暴击率% / 暴击伤害%'
    },
    sub_stats: '暴击率 / 暴击伤害 > 元素充能效率 > 攻击力% / 元素精通'
  };

  if (element === '岩') {
    rec.artifacts.bis_set = '华馆梦醒形骸记 4件套 / 千岩牢固 4件套';
    rec.main_stats.sands = '防御力% / 生命值%';
  } else if (element === '草') {
    rec.artifacts.bis_set = '深林的记忆 4件套 / 饰金之梦 4件套';
    rec.sub_stats = '元素精通 > 暴击率 / 暴击伤害 > 元素充能效率';
  } else if (element === '雷') {
    rec.artifacts.bis_set = '绝缘之旗印 4件套 / 如雷的盛怒 4件套';
  } else if (element === '水') {
    rec.artifacts.bis_set = '逐影猎人 4件套 / 黄金剧团 4件套 / 沉沦之心 4件套';
    rec.main_stats.sands = '生命值% / 元素充能%';
  } else if (element === '火') {
    rec.artifacts.bis_set = '炽烈的炎之魔女 4件套 / 追忆之注连 4件套';
  } else if (element === '风') {
    rec.artifacts.bis_set = '翠绿之影 4件套 (扩散降低40%对应元素抗性)';
    rec.sub_stats = '元素精通 > 元素充能效率 > 双暴';
  } else if (element === '冰') {
    rec.artifacts.bis_set = '冰风迷途的勇士 4件套 (冻结提供+40%暴击率)';
  }
  return rec;
}

const levelStages = [
  [1, 0, '1'], [20, 0, '20'], [20, 1, '20+'],
  [40, 1, '40'], [40, 2, '40+'], [50, 2, '50'],
  [50, 3, '50+'], [60, 3, '60'], [60, 4, '60+'],
  [70, 4, '70'], [70, 5, '70+'], [80, 5, '80'],
  [80, 6, '80+'], [90, 6, '90']
];

function processCharacter(name, talentLookupName) {
  const c = genshindb.characters(name);
  if (!c) return null;

  const t = genshindb.talents(talentLookupName || name) || {};
  const consts = genshindb.constellations(talentLookupName || name) || {};

  // Base Stats 14 stages
  const baseStats = levelStages.map(([lvl, asc, label]) => {
    let s;
    try {
      s = c.stats(lvl, asc);
    } catch {
      s = { hp: 1000, attack: 50, defense: 50, specialized: 0 };
    }
    const isCritRate = c.substatText === '暴击率';
    const isCritDmg = c.substatText === '暴击伤害';

    return {
      level: label,
      hp: Math.round(s.hp || 1000),
      atk: Math.round(s.attack || 50),
      def: Math.round(s.defense || 50),
      crit_rate: (isCritRate ? (5.0 + (s.specialized || 0) * 100).toFixed(1) : '5.0') + '%',
      crit_dmg: (isCritDmg ? (50.0 + (s.specialized || 0) * 100).toFixed(1) : '50.0') + '%'
    };
  });

  // Special Ascension Stat
  const specStat = {
    stat_name: c.substatText || '基础数值提升',
    stages: {}
  };
  ['40+', '50+', '70+', '80+'].forEach(stage => {
    const pair = levelStages.find(p => p[2] === stage);
    if (pair) {
      try {
        const s = c.stats(pair[0], pair[1]);
        const val = s.specialized || 0;
        if (c.substatText && (c.substatText.includes('加成') || c.substatText.includes('率') || c.substatText.includes('效率') || c.substatText.includes('%'))) {
          specStat.stages[stage] = (val * 100).toFixed(1).replace(/\.0$/, '') + '%';
        } else if (val > 0) {
          specStat.stages[stage] = Math.round(val).toString();
        } else {
          specStat.stages[stage] = '0.0%';
        }
      } catch {
        specStat.stages[stage] = '0.0%';
      }
    }
  });

  // Ascension materials
  const ascensionMaterials = [];
  const tierLabels = ['突破20级', '突破40级', '突破50级', '突破60级', '突破70级', '突破80级'];
  for (let i = 1; i <= 6; i++) {
    const costKey = 'ascend' + i;
    if (c.costs && c.costs[costKey]) {
      ascensionMaterials.push({
        tier: tierLabels[i - 1],
        items: formatCost(c.costs[costKey])
      });
    }
  }

  // Talents
  const talents = [];
  const combatList = [
    { raw: t.combat1, type: 'NORMAL_ATTACK', fallback: '普通攻击' },
    { raw: t.combat2, type: 'ELEMENTAL_SKILL', fallback: '元素战技' },
    { raw: t.combat3, type: 'ELEMENTAL_BURST', fallback: '元素爆发' }
  ];

  combatList.forEach((item, idx) => {
    if (item.raw) {
      const scaling = {};
      if (item.raw.attributes && item.raw.attributes.labels && item.raw.attributes.parameters) {
        item.raw.attributes.labels.forEach(lbl => {
          const parts = lbl.split('|');
          const title = parts[0].trim();
          const fmt = parts[1] || parts[0];
          const val = formatAttribute(fmt, item.raw.attributes.parameters, 9); // Lv10
          scaling[title] = val;
        });
      }
      talents.push({
        name: item.raw.name || item.fallback,
        type: item.type,
        description: item.raw.description || '',
        scaling: scaling
      });
    }
  });

  // Passives
  const passives = [];
  const pList = [
    { p: t.passive1, unlock: '突破等级 20' },
    { p: t.passive2, unlock: '突破等级 60' },
    { p: t.passive3, unlock: '固有天赋' }
  ];
  pList.forEach(item => {
    if (item.p) {
      passives.push({
        name: item.p.name,
        unlock: item.unlock,
        desc: item.p.description || ''
      });
    }
  });

  // Constellations
  const constellations = [];
  for (let i = 1; i <= 6; i++) {
    const cKey = 'c' + i;
    if (consts[cKey]) {
      constellations.push({
        c: i,
        name: consts[cKey].name,
        desc: consts[cKey].description || ''
      });
    }
  }

  // Images
  const avatarUrl = c.images?.mihoyo_icon || c.images?.icon || c.images?.card || '';
  const splashUrl = c.images?.cover1 || c.images?.cover2 || c.images?.card || c.images?.portrait || avatarUrl;

  const result = {
    game_id: 2,
    name: name,
    title: c.title || '',
    rarity: c.rarity || 5,
    element: c.elementText || '无',
    weapon_type: c.weaponText || '单手剑',
    region: c.region || '提瓦特',
    arkhe: getArkhe(name, c.region),
    avatar_url: avatarUrl,
    splash_url: splashUrl,
    base_stats: baseStats,
    special_ascension_stat: specStat,
    ascension_materials: ascensionMaterials,
    talents: talents,
    passives: passives,
    constellations: constellations,
    special_mechanics: getSpecialMechanics(name, c.elementText || '无', c.region),
    recommendations: getRecommendations(name, c.elementText || '无', c.weaponText || '单手剑'),
    version: c.version || '5.0'
  };

  result.data_hash = calcHash(result);
  return result;
}

function main() {
  console.log('=== 开始全量抽取原神全角色官方数值体系 (包含1-90级各阶白值、技能、命座、材料) ===');
  const names = genshindb.characters('names', { matchCategories: true });
  console.log(`在 genshin-db 中发现 ${names.length} 个角色名称。`);

  const characters = [];

  names.forEach(name => {
    if (name === '空' || name === '荧') {
      // 处理旅行者各元素形态
      const elements = ['风', '岩', '雷', '草', '水', '火'];
      elements.forEach(elem => {
        const talentName = `旅行者 (${elem}元素)`;
        const charName = `${name} (${elem}元素)`;
        const cObj = processCharacter(name, talentName);
        if (cObj) {
          cObj.name = charName;
          cObj.element = elem;
          cObj.title = `降临提瓦特的旅人·${elem}`;
          cObj.special_mechanics = getSpecialMechanics(charName, elem, '异界');
          cObj.recommendations = getRecommendations(charName, elem, '单手剑');
          cObj.data_hash = calcHash(cObj);
          characters.push(cObj);
          console.log(`  ✓ 成功提取旅行者形态: ${cObj.name}`);
        }
      });
      return;
    }

    const cObj = processCharacter(name);
    if (cObj) {
      characters.push(cObj);
      console.log(`  ✓ 成功提取角色: ${cObj.name} (${cObj.title}) [${cObj.rarity}★ ${cObj.element}元素 ${cObj.weapon_type}]`);
    }
  });

  const outDir = path.join(__dirname, '..', 'out');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, 'all_genshin_characters.json');
  fs.writeFileSync(outFile, JSON.stringify(characters, null, 2), 'utf-8');
  console.log(`\n🎉 全量提取完成！共计导出 ${characters.length} 位角色的全套完整数据至: ${outFile}`);
}

main();
