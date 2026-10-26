"""
Generate high-resolution SVG artwork for Naraka: Bladepoint (Game 20)
Heroes, Weapons, and Souljades.
"""

import os

HERO_META = {
    '宁红夜': {'color': ('#7f1d1d', '#b91c1c', '#f87171'), 'symbol': '红', 'role': '控场核心', 'en': 'Viper Ning'},
    '特木尔': {'color': ('#14532d', '#15803d', '#4ade80'), 'symbol': '狼', 'role': '风暴控场', 'en': 'Temulch'},
    '迦南': {'color': ('#581c87', '#7e22ce', '#c084fc'), 'symbol': '迦', 'role': '隐匿刺客', 'en': 'Matari'},
    '季沧海': {'color': ('#7c2d12', '#c2410c', '#fb923c'), 'symbol': '火', 'role': '狂暴输出', 'en': 'Tarka Ji'},
    '土御门胡桃': {'color': ('#831843', '#be185d', '#f472b6'), 'symbol': '桃', 'role': '仙术治疗', 'en': 'Kurumi'},
    '天海': {'color': ('#713f12', '#a16207', '#facc15'), 'symbol': '佛', 'role': '金刚坦克', 'en': 'Tianhai'},
    '妖刀姬': {'color': ('#881337', '#be123c', '#fb7185'), 'symbol': '妖', 'role': '重斩狂刀', 'en': 'Yoto Hime'},
    '崔三娘': {'color': ('#0c4a6e', '#0284c7', '#38bdf8'), 'symbol': '水', 'role': '狂澜控场', 'en': 'Valda Cui'},
    '岳山': {'color': ('#365314', '#4d7c0f', '#a3e635'), 'symbol': '岳', 'role': '破阵神将', 'en': 'Yueshan'},
    '无尘': {'color': ('#134e4a', '#0f766e', '#2dd4bf'), 'symbol': '道', 'role': '两仪传送', 'en': 'Wuchen'},
    '顾清寒': {'color': ('#164e63', '#0891b2', '#22d3ee'), 'symbol': '雪', 'role': '冰霜刺客', 'en': 'Justina Gu'},
    '武田信忠': {'color': ('#4c1d95', '#6d28d9', '#a78bfa'), 'symbol': '武', 'role': '封魔夺刀', 'en': 'Takeda'},
    '殷紫萍': {'color': ('#064e3b', '#059669', '#34d399'), 'symbol': '萍', 'role': '起死回生', 'en': 'Ziping Yin'},
    '沈妙': {'color': ('#701a75', '#a21caf', '#e879f9'), 'symbol': '妙', 'role': '机甲轰炸', 'en': 'Shen Miao'},
    '胡为': {'color': ('#78350f', '#b45309', '#f59e0b'), 'symbol': '虎', 'role': '狂虎突进', 'en': 'Hu Wei'},
    '季莹莹': {'color': ('#4c0519', '#9f1239', '#fb7185'), 'symbol': '莹', 'role': '幽冥链刃', 'en': 'Zai'},
    '玉玲珑': {'color': ('#500724', '#9d174d', '#f472b6'), 'symbol': '狐', 'role': '迷魂魅惑', 'en': 'Tessa'},
    '哈迪': {'color': ('#1f2937', '#4b5563', '#9ca3af'), 'symbol': '翼', 'role': '空中突刺', 'en': 'Hadi'},
    '魏轻': {'color': ('#1e1b4b', '#4338ca', '#818cf8'), 'symbol': '魏', 'role': '玄武正气', 'en': 'Wei Qing'},
    '刘炼': {'color': ('#3f2c18', '#78350f', '#d97706'), 'symbol': '炼', 'role': '金石熔炼', 'en': 'Liu Lian'},
    '张起灵': {'color': ('#09090b', '#27272a', '#a1a1aa'), 'symbol': '灵', 'role': '发丘黑金', 'en': 'Zhang Qiling'},
    '席拉': {'color': ('#713f12', '#ca8a04', '#fde047'), 'symbol': '光', 'role': '光辉治疗', 'en': 'Cyra'},
    '万钧': {'color': ('#1e1b4b', '#3730a3', '#818cf8'), 'symbol': '雷', 'role': '万钧破阵', 'en': 'Wan Jun'},
    '司南': {'color': ('#134e4a', '#0d9488', '#5eead4'), 'symbol': '南', 'role': '磁场掌控', 'en': 'Si Nan'},
    '赛特': {'color': ('#451a03', '#92400e', '#f59e0b'), 'symbol': '沙', 'role': '黄沙潜袭', 'en': 'Seth'},
    '白泽': {'color': ('#083344', '#0e7490', '#67e8f9'), 'symbol': '泽', 'role': '祥瑞庇佑', 'en': 'Bai Ze'},
    '墨羽': {'color': ('#18181b', '#3f3f46', '#e4e4e7'), 'symbol': '墨', 'role': '水墨穿梭', 'en': 'Mo Yu'},
    '灵狐仙子': {'color': ('#831843', '#db2777', '#f472b6'), 'symbol': '仙', 'role': '九尾魅影', 'en': 'Nine-Tailed'},
    '刑天': {'color': ('#7f1d1d', '#dc2626', '#f87171'), 'symbol': '战', 'role': '战神霸体', 'en': 'Xing Tian'},
    '李白': {'color': ('#172554', '#1d4ed8', '#60a5fa'), 'symbol': '白', 'role': '青莲剑仙', 'en': 'Li Bai'},
    '孙悟空': {'color': ('#78350f', '#d97706', '#fde047'), 'symbol': '空', 'role': '齐天大圣', 'en': 'Sun Wukong'},
    '蓝梦': {'color': ('#0c4a6e', '#0284c7', '#7dd3fc'), 'symbol': '梦', 'role': '幻海潮生', 'en': 'Lan Meng'},
}

WEAPONS_META = {
    '太刀': {'color': ('#881337', '#be123c', '#fb7185'), 'icon': '🗡️', 'en': 'Katana', 'type': '近战 · 极速百裂斩'},
    '长剑': {'color': ('#1e3a8a', '#2563eb', '#93c5fd'), 'icon': '⚔️', 'en': 'Longsword', 'type': '近战 · 剑气纵横'},
    '阔刀': {'color': ('#78350f', '#d97706', '#fde047'), 'icon': '🪓', 'en': 'Greatsword', 'type': '近战 · 磐石反击'},
    '斩马刀': {'color': ('#7f1d1d', '#dc2626', '#fca5a5'), 'icon': '🗡️', 'en': 'Zhanmadao', 'type': '近战 · 战马断月斩'},
    '长枪': {'color': ('#064e3b', '#059669', '#6ee7b7'), 'icon': '🔱', 'en': 'Spear', 'type': '近战 · 龙王破哪吒闹海'},
    '棍': {'color': ('#854d0e', '#ca8a04', '#fef08a'), 'icon': '🥢', 'en': 'Staff', 'type': '近战 · 定海定风棍'},
    '双节棍': {'color': ('#4c1d95', '#7c3aed', '#c4b5fd'), 'icon': '⛓️', 'en': 'Nunchucks', 'type': '近战 · 横打横踢龙虎乱舞'},
    '双刀': {'color': ('#164e63', '#0891b2', '#67e8f9'), 'icon': '⚔️', 'en': 'Dual Blades', 'type': '近战 · 剪刀绝技乾坤日月'},
    '双戟': {'color': ('#831843', '#db2777', '#fbcfe8'), 'icon': '🔱', 'en': 'Dual Halberds', 'type': '近战 · 破千军蛟龙翻江'},
    '扇': {'color': ('#134e4a', '#0d9488', '#99f6e4'), 'icon': '🪭', 'en': 'Fan', 'type': '近战 · 问天罡卷风流'},
    '匕首': {'color': ('#4c0519', '#9f1239', '#fecdd3'), 'icon': '🔪', 'en': 'Dagger', 'type': '近战 · 闪步荆轲献匕'},
    '拳刃': {'color': ('#701a75', '#c026d3', '#f5d0fe'), 'icon': '🥊', 'en': 'Fist Blades', 'type': '近战 · 贴身搏击寸劲'},
    '横刀': {'color': ('#1e1b4b', '#4338ca', '#a5b4fc'), 'icon': '🗡️', 'en': 'Hengdao', 'type': '近战 · 唐刀极意破空斩'},
    '鸟铳': {'color': ('#3f2c18', '#b45309', '#fcd34d'), 'icon': '🔫', 'en': 'Musket', 'type': '远程 · 高伤狙杀爆头'},
    '弓箭': {'color': ('#14532d', '#16a34a', '#86efac'), 'icon': '🏹', 'en': 'Bow', 'type': '远程 · 蓄力散射二段引力'},
    '火炮': {'color': ('#7c2d12', '#ea580c', '#fdba74'), 'icon': '💣', 'en': 'Cannon', 'type': '远程 · 范围轰炸反弹'},
    '五眼铳': {'color': ('#374151', '#4b5563', '#d1d5db'), 'icon': '🔥', 'en': 'Repeating Crossbow', 'type': '远程 · 近距散弹瞬间爆发'},
    '连弩': {'color': ('#155e75', '#0284c7', '#7dd3fc'), 'icon': '🎯', 'en': 'Crossbow', 'type': '远程 · 极速连射压制'},
    '一窝蜂': {'color': ('#991b1b', '#ef4444', '#fca5a5'), 'icon': '🚀', 'en': 'Swarm Rocket', 'type': '空投神器 · 火箭齐射'},
    '喷火筒': {'color': ('#9a3412', '#f97316', '#fed7aa'), 'icon': '🔥', 'en': 'Flamebringer', 'type': '空投神器 · 持续真火灼烧'},
}

SOULJADE_META = {
    '夺魂·近战': {'color': ('#7f1d1d', '#dc2626', '#fca5a5'), 'glyph': '魂', 'type': '极品近战神玉', 'en': 'Soul Siphon'},
    '毕工淌': {'color': ('#14532d', '#16a34a', '#86efac'), 'glyph': '修', 'type': '特品功能神玉', 'en': 'Quick Fix'},
    '凌波': {'color': ('#0c4a6e', '#0284c7', '#7dd3fc'), 'glyph': '波', 'type': '移动身法神玉', 'en': 'Wave Step'},
    '虚影步': {'color': ('#581c87', '#9333ea', '#d8b4fe'), 'glyph': '影', 'type': '极品身法神玉', 'en': 'Phantom Step'},
    '噬魂斩': {'color': ('#881337', '#be123c', '#fda4af'), 'glyph': '斩', 'type': '太刀专属神玉', 'en': 'Soul Slash'},
    '凤凰羽': {'color': ('#991b1b', '#ef4444', '#fecaca'), 'glyph': '羽', 'type': '长剑专属神玉', 'en': 'Phoenix Plume'},
    '烈火斩': {'color': ('#7c2d12', '#ea580c', '#ffedd5'), 'glyph': '烈', 'type': '阔刀专属神玉', 'en': 'Fiery Slash'},
    '过关斩将': {'color': ('#78350f', '#d97706', '#fef3c7'), 'glyph': '将', 'type': '斩马刀专属神玉', 'en': 'Zhanmadao Strike'},
    '狂浪怒涛': {'color': ('#164e63', '#0891b2', '#cffafe'), 'glyph': '浪', 'type': '长枪专属神玉', 'en': 'Raging Waves'},
    '龙虎乱舞': {'color': ('#4c1d95', '#7c3aed', '#ede9fe'), 'glyph': '龙', 'type': '双节棍专属神玉', 'en': 'Dragon Tiger'},
    '乾坤日月斩': {'color': ('#1e1b4b', '#4338ca', '#e0e7ff'), 'glyph': '坤', 'type': '双刀专属神玉', 'en': 'Dual Blades Slash'},
    '极乐汤': {'color': ('#134e4a', '#0d9488', '#ccfbf1'), 'glyph': '乐', 'type': '扇专属神玉', 'en': 'Fan Whirl'},
    '幽冥步': {'color': ('#4c0519', '#9f1239', '#ffe4e6'), 'glyph': '冥', 'type': '匕首专属神玉', 'en': 'Shadow Step'},
    '召雷术': {'color': ('#312e81', '#4f46e5', '#c7d2fe'), 'glyph': '雷', 'type': '天地绝技神玉', 'en': 'Thunder Call'},
    '续命术': {'color': ('#064e3b', '#059669', '#a7f3d0'), 'glyph': '生', 'type': '庇佑防守神玉', 'en': 'Life Prolong'},
    '易武·万方': {'color': ('#713f12', '#ca8a04', '#fef9c3'), 'glyph': '武', 'type': '流派切换神玉', 'en': 'Quick Swap'},
    '鬼哭神嚎': {'color': ('#3b0764', '#7e22ce', '#e9d5ff'), 'glyph': '鬼', 'type': '匕首神级绝技', 'en': 'Ghost Howl'},
    '暴凌': {'color': ('#831843', '#db2777', '#fce7f3'), 'glyph': '暴', 'type': '近战强攻神玉', 'en': 'Brutal Strike'},
    '极光碎云闪': {'color': ('#172554', '#2563eb', '#bfdbfe'), 'glyph': '极', 'type': '长剑极品神玉', 'en': 'Aurora Flash'},
    '风火穿心脚': {'color': ('#9a3412', '#f97316', '#ffedd5'), 'glyph': '风', 'type': '双节棍极品神玉', 'en': 'Windfire Kick'},
}


def build_hero_svg(name, meta):
    c1, c2, c3 = meta['color']
    symbol = meta['symbol']
    role = meta['role']
    en = meta['en']

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="100%" height="100%">
  <defs>
    <radialGradient id="bg" cx="50%" cy="40%" r="65%">
      <stop offset="0%" stop-color="{c2}" stop-opacity="0.9" />
      <stop offset="70%" stop-color="{c1}" stop-opacity="1" />
      <stop offset="100%" stop-color="#0a0a0c" stop-opacity="1" />
    </radialGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a" />
      <stop offset="50%" stop-color="#eab308" />
      <stop offset="100%" stop-color="#854d0e" />
    </linearGradient>
    <linearGradient id="charGlow" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="100%" stop-color="{c3}" />
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.8" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="256" height="256" rx="44" fill="url(#bg)" />
  <rect width="252" height="252" x="2" y="2" rx="42" fill="none" stroke="url(#gold)" stroke-width="2.5" opacity="0.6" />
  
  <!-- Outer Decorative Ring -->
  <circle cx="128" cy="116" r="76" fill="none" stroke="{c3}" stroke-width="1.5" stroke-dasharray="6 4" opacity="0.4" />
  <circle cx="128" cy="116" r="66" fill="none" stroke="url(#gold)" stroke-width="2" opacity="0.7" />
  
  <!-- Eight Trigrams / Martial Corner Accents -->
  <path d="M 60 48 L 48 48 L 48 60" fill="none" stroke="url(#gold)" stroke-width="2" opacity="0.8" />
  <path d="M 196 48 L 208 48 L 208 60" fill="none" stroke="url(#gold)" stroke-width="2" opacity="0.8" />
  <path d="M 60 208 L 48 208 L 48 196" fill="none" stroke="url(#gold)" stroke-width="2" opacity="0.8" />
  <path d="M 196 208 L 208 208 L 208 196" fill="none" stroke="url(#gold)" stroke-width="2" opacity="0.8" />

  <!-- Center Martial Seal Calligraphy Character -->
  <text x="128" y="148" font-family="'PingFang SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif" font-weight="900" font-size="78" fill="url(#charGlow)" text-anchor="middle" filter="url(#shadow)">{symbol}</text>

  <!-- Top Badge: Role -->
  <g transform="translate(128, 38)">
    <rect x="-42" y="-12" width="84" height="20" rx="10" fill="#000000" fill-opacity="0.65" stroke="{c3}" stroke-width="1" />
    <text x="0" y="2" font-family="'PingFang SC', sans-serif" font-weight="bold" font-size="10.5" fill="{c3}" text-anchor="middle">{role}</text>
  </g>

  <!-- Bottom Name & English Subtitle Plate -->
  <g transform="translate(128, 218)">
    <rect x="-65" y="-18" width="130" height="28" rx="8" fill="#09090b" fill-opacity="0.85" stroke="url(#gold)" stroke-width="1.2" />
    <text x="0" y="-3" font-family="'PingFang SC', sans-serif" font-weight="bold" font-size="13" fill="#ffffff" text-anchor="middle">{name}</text>
    <text x="0" y="8" font-family="sans-serif" font-weight="500" font-size="8" fill="#a1a1aa" text-anchor="middle">{en}</text>
  </g>
</svg>'''


def build_weapon_svg(name, meta):
    c1, c2, c3 = meta['color']
    icon = meta['icon']
    wtype = meta['type']
    en = meta['en']

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="100%" height="100%">
  <defs>
    <radialGradient id="wbg" cx="50%" cy="45%" r="65%">
      <stop offset="0%" stop-color="{c2}" stop-opacity="0.85" />
      <stop offset="60%" stop-color="{c1}" stop-opacity="0.95" />
      <stop offset="100%" stop-color="#09090b" stop-opacity="1" />
    </radialGradient>
    <linearGradient id="wgold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a" />
      <stop offset="50%" stop-color="#eab308" />
      <stop offset="100%" stop-color="#713f12" />
    </linearGradient>
    <filter id="wshadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.75" />
    </filter>
  </defs>

  <!-- Card background -->
  <rect width="256" height="256" rx="40" fill="url(#wbg)" />
  <rect width="250" height="250" x="3" y="3" rx="37" fill="none" stroke="url(#wgold)" stroke-width="2" opacity="0.6" />

  <!-- Blades / Crosshairs decorative background -->
  <circle cx="128" cy="112" r="70" fill="none" stroke="{c3}" stroke-width="1.5" stroke-dasharray="4 6" opacity="0.4" />
  <circle cx="128" cy="112" r="54" fill="#000000" fill-opacity="0.3" stroke="url(#wgold)" stroke-width="1.5" />

  <!-- Weapon Icon & Calligraphy -->
  <text x="128" y="118" font-size="54" text-anchor="middle" filter="url(#wshadow)">{icon}</text>
  <text x="128" y="152" font-family="'PingFang SC', 'Noto Serif SC', serif" font-weight="900" font-size="20" fill="#ffffff" text-anchor="middle" filter="url(#wshadow)">{name}</text>

  <!-- Weapon Type Badge -->
  <g transform="translate(128, 38)">
    <rect x="-60" y="-12" width="120" height="20" rx="10" fill="#000000" fill-opacity="0.7" stroke="{c3}" stroke-width="1" />
    <text x="0" y="2" font-family="'PingFang SC', sans-serif" font-weight="bold" font-size="10" fill="{c3}" text-anchor="middle">{wtype.split('·')[0].strip()}</text>
  </g>

  <!-- Bottom Plate -->
  <g transform="translate(128, 218)">
    <rect x="-70" y="-18" width="140" height="28" rx="8" fill="#0c0a09" fill-opacity="0.9" stroke="url(#wgold)" stroke-width="1" />
    <text x="0" y="-2" font-family="'PingFang SC', sans-serif" font-weight="bold" font-size="11" fill="#fef08a" text-anchor="middle">{wtype}</text>
    <text x="0" y="8" font-family="sans-serif" font-weight="500" font-size="8" fill="#a8a29e" text-anchor="middle">{en}</text>
  </g>
</svg>'''


def build_souljade_svg(name, meta):
    c1, c2, c3 = meta['color']
    glyph = meta['glyph']
    stype = meta['type']
    en = meta['en']

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="100%" height="100%">
  <defs>
    <radialGradient id="jbg" cx="50%" cy="45%" r="65%">
      <stop offset="0%" stop-color="{c2}" stop-opacity="0.9" />
      <stop offset="60%" stop-color="{c1}" stop-opacity="1" />
      <stop offset="100%" stop-color="#050507" stop-opacity="1" />
    </radialGradient>
    <radialGradient id="jadeCore" cx="45%" cy="40%" r="55%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.4" />
      <stop offset="40%" stop-color="{c3}" stop-opacity="0.85" />
      <stop offset="100%" stop-color="{c1}" stop-opacity="0.95" />
    </radialGradient>
    <linearGradient id="jgold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef9c3" />
      <stop offset="50%" stop-color="#facc15" />
      <stop offset="100%" stop-color="#a16207" />
    </linearGradient>
    <filter id="jshadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.8" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="256" height="256" rx="44" fill="url(#jbg)" />
  <rect width="250" height="250" x="3" y="3" rx="41" fill="none" stroke="url(#jgold)" stroke-width="2" opacity="0.5" />

  <!-- Jade Medallion Outer Filigree Ring -->
  <circle cx="128" cy="112" r="68" fill="none" stroke="url(#jgold)" stroke-width="4" filter="url(#jshadow)" />
  <circle cx="128" cy="112" r="62" fill="none" stroke="{c3}" stroke-width="1.5" stroke-dasharray="5 3" opacity="0.6" />
  
  <!-- Glowing Jade Inner Disc -->
  <circle cx="128" cy="112" r="56" fill="url(#jadeCore)" stroke="url(#jgold)" stroke-width="2" />
  <circle cx="128" cy="112" r="22" fill="#000000" fill-opacity="0.35" stroke="url(#jgold)" stroke-width="1" />

  <!-- Center Ancient Sigil Glyph -->
  <text x="128" y="126" font-family="'PingFang SC', 'Noto Serif SC', 'Kaiti SC', serif" font-weight="900" font-size="40" fill="#ffffff" text-anchor="middle" filter="url(#jshadow)">{glyph}</text>

  <!-- Top Badge -->
  <g transform="translate(128, 32)">
    <rect x="-48" y="-11" width="96" height="19" rx="9" fill="#000000" fill-opacity="0.75" stroke="{c3}" stroke-width="1" />
    <text x="0" y="2.5" font-family="'PingFang SC', sans-serif" font-weight="bold" font-size="9.5" fill="{c3}" text-anchor="middle">{stype}</text>
  </g>

  <!-- Bottom Name Banner -->
  <g transform="translate(128, 218)">
    <rect x="-65" y="-18" width="130" height="28" rx="8" fill="#09090b" fill-opacity="0.9" stroke="url(#jgold)" stroke-width="1.2" />
    <text x="0" y="-3" font-family="'PingFang SC', sans-serif" font-weight="bold" font-size="12" fill="#fef08a" text-anchor="middle">{name}</text>
    <text x="0" y="8" font-family="sans-serif" font-weight="500" font-size="8" fill="#a1a1aa" text-anchor="middle">{en}</text>
  </g>
</svg>'''


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'games'))
    hero_dir = os.path.join(base_dir, 'naraka')
    weapon_dir = os.path.join(base_dir, 'naraka_weapons')
    souljade_dir = os.path.join(base_dir, 'souljades')

    os.makedirs(hero_dir, exist_ok=True)
    os.makedirs(weapon_dir, exist_ok=True)
    os.makedirs(souljade_dir, exist_ok=True)

    print(f'[Assets] Generating {len(HERO_META)} hero SVGs in {hero_dir}...')
    for name, meta in HERO_META.items():
        svg_content = build_hero_svg(name, meta)
        path = os.path.join(hero_dir, f'{name}.svg')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        # Also write .png fallback alias or link if needed
        # By having .svg we can point crawler to .svg or .png with fallback

    print(f'[Assets] Generating {len(WEAPONS_META)} weapon SVGs in {weapon_dir}...')
    for name, meta in WEAPONS_META.items():
        svg_content = build_weapon_svg(name, meta)
        path = os.path.join(weapon_dir, f'{name}.svg')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

    print(f'[Assets] Generating {len(SOULJADE_META)} souljade SVGs in {souljade_dir}...')
    for name, meta in SOULJADE_META.items():
        svg_content = build_souljade_svg(name, meta)
        path = os.path.join(souljade_dir, f'{name}.svg')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

    print('[Assets] All Naraka SVGs generated successfully!')


if __name__ == '__main__':
    main()
