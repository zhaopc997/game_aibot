const fs = require('fs');
const path = require('path');
const genshin = require('genshin-db');

genshin.setOptions({ resultLanguage: 'CHS', queryLanguages: ['CHS', 'EN'] });

const outDir = path.resolve(__dirname, '../out');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

// -------------------------------------------------------------
// 1. Export All Weapons
// -------------------------------------------------------------
console.log('--- 正在导出全量武器数据 ---');
const weaponNames = genshin.weapons('names', { matchCategories: true });
console.log(`检索到武器总数: ${weaponNames.length}`);

const levels = [1, 20, 40, 50, 60, 70, 80, 90];
const weaponsList = [];

for (const name of weaponNames) {
  const w = genshin.weapons(name);
  if (!w) {
    console.warn(`未找到武器数据: ${name}`);
    continue;
  }

  // 1. 基础攻击力曲线
  const baseAtkCurve = [];
  const subStatValues = {};

  for (const lvl of levels) {
    const st = w.stats(lvl);
    if (!st) continue;

    baseAtkCurve.push({
      level: String(lvl),
      atk: Math.round(st.attack || 0)
    });

    if (w.mainStatText && st.specialized !== undefined && st.specialized !== null) {
      if (w.mainStatText === '元素精通') {
        subStatValues[String(lvl)] = String(Math.round(st.specialized));
      } else {
        subStatValues[String(lvl)] = (st.specialized * 100).toFixed(1) + '%';
      }
    }
  }

  // 2. 副词条
  let subStat = {};
  if (w.mainStatText) {
    let statName = w.mainStatText;
    if (['攻击力', '生命值', '防御力'].includes(statName)) {
      statName = statName + '百分比';
    }
    subStat = {
      stat_name: statName,
      values: subStatValues
    };
  }

  // 3. 精炼效果
  const refinements = [];
  const refineKeys = ['r1', 'r2', 'r3', 'r4', 'r5'];
  for (let i = 0; i < refineKeys.length; i++) {
    const rObj = w[refineKeys[i]];
    if (rObj && rObj.description) {
      refinements.push({
        rank: `精炼 ${i + 1}阶`,
        desc: rObj.description
      });
    }
  }

  // 4. 突破材料
  const ascensionMaterials = [];
  if (w.costs) {
    const tierMap = {
      ascend1: '突破20级',
      ascend2: '突破40级',
      ascend3: '突破50级',
      ascend4: '突破60级',
      ascend5: '突破70级',
      ascend6: '突破80级'
    };
    for (const [key, label] of Object.entries(tierMap)) {
      if (w.costs[key] && Array.isArray(w.costs[key])) {
        const itemStr = w.costs[key].map(it => `${it.name} x${it.count}`).join(', ');
        ascensionMaterials.push({
          tier: label,
          items: itemStr
        });
      }
    }
  }

  // 5. 图标
  const iconUrl = w.images?.mihoyo_icon || w.images?.icon || '';

  weaponsList.push({
    name: w.name,
    type: w.weaponText || '单手剑',
    rarity: w.rarity || 4,
    icon_url: iconUrl,
    base_atk_curve: baseAtkCurve,
    sub_stat: subStat,
    refinements: refinements,
    ascension_materials: ascensionMaterials,
    version: '5.0'
  });
}

const weaponOutPath = path.resolve(outDir, 'all_genshin_weapons.json');
fs.writeFileSync(weaponOutPath, JSON.stringify(weaponsList, null, 2), 'utf-8');
console.log(`成功导出 ${weaponsList.length} 把武器到: ${weaponOutPath}`);


// -------------------------------------------------------------
// 2. Export All Artifact Sets
// -------------------------------------------------------------
console.log('\n--- 正在导出全量圣遗物套装数据 ---');
const artifactNames = genshin.artifacts('names', { matchCategories: true });
console.log(`检索到圣遗物套装总数: ${artifactNames.length}`);

const artifactsList = [];

for (const name of artifactNames) {
  const a = genshin.artifacts(name);
  if (!a) {
    console.warn(`未找到圣遗物数据: ${name}`);
    continue;
  }

  const rarityList = Array.isArray(a.rarityList) ? a.rarityList : [4, 5];
  const rarityMin = Math.min(...rarityList);
  const rarityMax = Math.max(...rarityList);

  const slotMap = [
    { key: 'flower', slot: '生之花', mainStat: '固定生命值 4780 (20级)' },
    { key: 'plume', slot: '死之羽', mainStat: '固定攻击力 311 (20级)' },
    { key: 'sands', slot: '时之沙', mainStat: '生命值% (46.6%) / 攻击力% (46.6%) / 防御力% (58.3%) / 充能% (51.8%) / 精通 (187)' },
    { key: 'goblet', slot: '空之杯', mainStat: '各属性伤害加成% (46.6%) / 物理伤害加成% (58.3%) / 攻击% / 生命% / 防御% / 精通' },
    { key: 'circlet', slot: '理之冠', mainStat: '暴击率% (31.1%) / 暴击伤害% (62.2%) / 治疗加成% (35.9%) / 攻击% / 生命% / 防御%' }
  ];

  const pieces = [];
  for (const s of slotMap) {
    if (a[s.key]) {
      const pieceName = typeof a[s.key] === 'object' ? a[s.key].name : a[s.key];
      const pieceIcon = a.images?.[`mihoyo_${s.key}`] || a.images?.[s.key] || '';
      pieces.push({
        slot: s.slot,
        name: pieceName || s.slot,
        icon_url: pieceIcon,
        main_stat_rule: s.mainStat
      });
    }
  }

  // 套装效果
  const twoPiece = a.effect2Pc || (a.effect1Pc ? `【1件套效果】${a.effect1Pc}` : '无');
  const fourPiece = a.effect4Pc || (a.effect1Pc ? '单件特殊圣遗物，无4件套效果。' : '无');

  // 图标选 flower 或者 circlet
  const setIcon = a.images?.mihoyo_flower || a.images?.flower || a.images?.mihoyo_circlet || a.images?.circlet || '';

  artifactsList.push({
    name: a.name,
    rarity_min: rarityMin,
    rarity_max: rarityMax,
    icon_url: setIcon,
    two_piece_bonus: twoPiece,
    four_piece_bonus: fourPiece,
    pieces: pieces,
    rules_reference: {
      sub_stat_pool: [
        '暴击率', '暴击伤害', '攻击力百分比', '元素充能效率',
        '元素精通', '生命值百分比', '防御力百分比',
        '固定攻击力', '固定生命值', '固定防御力'
      ],
      sub_stat_tiers_4star_and_5star: {
        crit_rate: ['2.7%', '3.1%', '3.5%', '3.9%'],
        crit_dmg: ['5.4%', '6.2%', '7.0%', '7.8%'],
        atk_percent: ['4.1%', '4.7%', '5.3%', '5.8%'],
        energy_recharge: ['4.5%', '5.2%', '5.8%', '6.5%'],
        elemental_mastery: [16, 19, 21, 23],
        hp_percent: ['4.1%', '4.7%', '5.3%', '5.8%'],
        def_percent: ['5.1%', '5.8%', '6.6%', '7.3%']
      }
    },
    version: '5.0'
  });
}

const artifactOutPath = path.resolve(outDir, 'all_genshin_artifacts.json');
fs.writeFileSync(artifactOutPath, JSON.stringify(artifactsList, null, 2), 'utf-8');
console.log(`成功导出 ${artifactsList.length} 套圣遗物到: ${artifactOutPath}`);
console.log('=== 全量装备数据导出完成！ ===');
