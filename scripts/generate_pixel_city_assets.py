#!/usr/bin/env python3
"""
Pixel City (指尖像素城) High-Fidelity SVG Visual Asset Generator
Generates retro-futuristic pixel-styled SVG graphics for 20 heroes, 12 relics, 6 rune sets, and cover.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PUBLIC = os.path.join(ROOT, 'frontend', 'public')

HERO_DIR = os.path.join(FRONTEND_PUBLIC, 'games', 'pixel_city')
RELIC_DIR = os.path.join(FRONTEND_PUBLIC, 'games', 'pixel_relics')
RUNE_DIR = os.path.join(FRONTEND_PUBLIC, 'games', 'pixel_runes')
GAMES_DIR = os.path.join(FRONTEND_PUBLIC, 'games')

for d in [HERO_DIR, RELIC_DIR, RUNE_DIR, GAMES_DIR]:
    os.makedirs(d, exist_ok=True)

HEROES = [
    ('qinglong', '青龙', '雷霆·虚空主C', '#0ea5e9', '#38bdf8', '#0284c7', '⚡'),
    ('kaguya', '辉夜姬', '月神·怒气压制', '#c084fc', '#e879f9', '#9333ea', '🌙'),
    ('yukionna', '雪女', '冰霜·极致减怒', '#38bdf8', '#7dd3fc', '#0284c7', '❄️'),
    ('volka', '沃尔卡', '烈焰·狂暴主C', '#f97316', '#fb923c', '#ea580c', '🔥'),
    ('phoenix', '凤凰', '烈焰·涅槃神佑', '#ef4444', '#f87171', '#dc2626', '🦅'),
    ('camilla', '卡米拉', '暗夜·破盾一刀', '#ec4899', '#f472b6', '#db2777', '🗡️'),
    ('taotie', '饕餮', '混沌·吞怒巨坦', '#84cc16', '#a3e635', '#65a30d', '🛡️'),
    ('athena', '雅典娜', '圣辉·长矛破盾', '#eab308', '#facc15', '#ca8a04', '✨'),
    ('horus', '荷鲁斯', '光辉·神明助战', '#f59e0b', '#fbbf24', '#d97706', '☀️'),
    ('venus', '维纳斯', '爱神·治愈魅惑', '#f43f5e', '#fb7185', '#e11d48', '💖'),
    ('luna', '露娜', '月影·暗夜暴伤', '#818cf8', '#a5b4fc', '#6366f1', '🔮'),
    ('igla', '伊格拉', '自然·生机增伤', '#10b981', '#34d399', '#059669', '🌿'),
    ('change', '嫦娥', '月宫·清辉沉睡', '#a855f7', '#c084fc', '#9333ea', '🪞'),
    ('sphinx', '斯芬克斯', '疾风·沉默风暴', '#06b6d4', '#22d3ee', '#0891b2', '🌪️'),
    ('titan', '泰坦', '大地·坚毅巨壁', '#78716c', '#a8a29e', '#57534e', '🗿'),
    ('luoshen', '洛神', '水月·潮汐净化', '#0284c7', '#38bdf8', '#0369a1', '🌊'),
    ('hela', '海拉', '冥界·死亡收割', '#64748b', '#94a3b8', '#475569', '💀'),
    ('tamamo', '玉藻前', '百妖·九尾回怒', '#f43f5e', '#fb7185', '#be123c', '🦊'),
    ('ikamonkey', '伊卡猴', '虚空·分身定身', '#d97706', '#f59e0b', '#b45309', '🐒'),
    ('september', '九月痕', '影刃·突刺灭怒', '#4f46e5', '#6366f1', '#4338ca', '⚔️')
]

RELICS = [
    ('eye_of_extinction', '终焉之眼', '虚空顶级圣物', '#0284c7', '#38bdf8', '👁️'),
    ('eternal_grail', '永恒圣杯', '神圣首发回怒', '#eab308', '#fde047', '🏆'),
    ('frost_snowflake', '寒冰雪花片', '冰冻概率翻倍', '#38bdf8', '#bae6fd', '❄️'),
    ('blazing_plume', '炎魔炽羽', '灼烧引爆圣物', '#ef4444', '#fca5a5', '🪶'),
    ('godslayer_blade', '弑神之刃', '低血斩杀圣物', '#ec4899', '#fbcfe8', '🗡️'),
    ('aegis_of_titan', '泰坦神盾', '护盾反伤圣器', '#78716c', '#d6d3d1', '🛡️'),
    ('lunaria_pendant', '月神吊坠', '受击偷取怒气', '#c084fc', '#f5d0fe', '📿'),
    ('orb_of_chaos', '混沌法球', '吞噬伤害转盾', '#84cc16', '#d9f99d', '🔮'),
    ('wings_of_ra', '太阳神圣翼', '助战全队免伤', '#f59e0b', '#fef08a', '🪽'),
    ('void_dawn_spear', '虚空破晓矛', '屏障破裂圣击', '#a855f7', '#e9d5ff', '🔱'),
    ('lingxiao_mirror', '灵霄玄天镜', '受控自动解控', '#06b6d4', '#cffafe', '🪞'),
    ('subduing_hoop', '定海金箍', '暴击必定眩晕', '#f97316', '#ffedd5', '💫')
]

RUNES = [
    ('burst_set', '爆裂符文套', '暴伤+50% 附带真实伤害', '#ef4444', '#f87171', '💥'),
    ('rage_suppress_set', '怒气压制套', '全员削减25怒气 增伤15%', '#8b5cf6', '#a78bfa', '⚡'),
    ('divine_barrier_set', '神圣屏障套', '开局35%生命上限屏障', '#eab308', '#fde047', '🛡️'),
    ('gale_combo_set', '疾风连击套', '普攻35%追加无消耗绝技', '#06b6d4', '#67e8f9', '🌪️'),
    ('void_soul_set', '虚空噬魂套', '击杀满额回怒 攻击+30%', '#ec4899', '#f472b6', '🔮'),
    ('echo_of_life_set', '生命回响套', '受疗+25% 护盾附带净化', '#10b981', '#34d399', '🌿')
]


def generate_hero_svg(key, name, role, c1, c2, c3, emoji):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <linearGradient id="bg_{key}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="50%" stop-color="#1e1b4b" />
      <stop offset="100%" stop-color="{c3}" stop-opacity="0.8" />
    </linearGradient>
    <linearGradient id="border_{key}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c2}" />
      <stop offset="100%" stop-color="{c1}" />
    </linearGradient>
    <filter id="glow_{key}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Pixel Pattern Grid Background -->
  <rect width="200" height="200" rx="16" fill="url(#bg_{key})" />
  <g opacity="0.15">
    <pattern id="grid_{key}" width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="5" height="5" fill="#ffffff" />
    </pattern>
    <rect width="200" height="200" rx="16" fill="url(#grid_{key})" />
  </g>

  <!-- Pixelated Frame Border -->
  <rect x="6" y="6" width="188" height="188" rx="12" fill="none" stroke="url(#border_{key})" stroke-width="4" />
  <rect x="12" y="12" width="176" height="176" rx="8" fill="none" stroke="{c2}" stroke-opacity="0.3" stroke-width="1.5" stroke-dasharray="4 2" />

  <!-- Pixel Corner Accents -->
  <rect x="10" y="10" width="8" height="8" fill="{c2}" />
  <rect x="182" y="10" width="8" height="8" fill="{c2}" />
  <rect x="10" y="182" width="8" height="8" fill="{c2}" />
  <rect x="182" y="182" width="8" height="8" fill="{c2}" />

  <!-- Center Pixel Art Emblem -->
  <circle cx="100" cy="85" r="46" fill="{c1}" fill-opacity="0.25" filter="url(#glow_{key})" />
  <polygon points="100,45 138,85 100,125 62,85" fill="none" stroke="{c2}" stroke-width="3" stroke-dasharray="6 3" />
  <text x="100" y="100" font-size="44" text-anchor="middle" dominant-baseline="middle">{emoji}</text>

  <!-- Level / Badge -->
  <g transform="translate(100, 142)">
    <rect x="-70" y="-14" width="140" height="28" rx="6" fill="#090d16" stroke="{c1}" stroke-width="2" />
    <text x="0" y="5" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="900" font-size="13" fill="#ffffff" text-anchor="middle">{name}</text>
  </g>

  <!-- Role Subtitle -->
  <text x="100" y="178" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="10" fill="{c2}" text-anchor="middle" letter-spacing="1">{role}</text>
</svg>
"""


def generate_relic_svg(key, name, role, c1, c2, emoji):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <linearGradient id="relic_bg_{key}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#18181b" />
      <stop offset="100%" stop-color="#27272a" />
    </linearGradient>
    <linearGradient id="relic_glow_{key}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c2}" />
      <stop offset="100%" stop-color="{c1}" />
    </linearGradient>
  </defs>

  <rect width="200" height="200" rx="14" fill="url(#relic_bg_{key})" />
  <rect x="8" y="8" width="184" height="184" rx="10" fill="none" stroke="url(#relic_glow_{key})" stroke-width="3.5" />
  
  <!-- Pixel Diamond -->
  <polygon points="100,32 152,84 100,136 48,84" fill="{c1}" fill-opacity="0.18" stroke="{c2}" stroke-width="2" />
  <text x="100" y="94" font-size="46" text-anchor="middle" dominant-baseline="middle">{emoji}</text>

  <!-- Name Plate -->
  <rect x="25" y="145" width="150" height="26" rx="6" fill="#09090b" stroke="{c1}" stroke-width="1.5" />
  <text x="100" y="162" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="800" font-size="12" fill="#ffffff" text-anchor="middle">{name}</text>
  <text x="100" y="186" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="600" font-size="9" fill="{c2}" text-anchor="middle">{role}</text>
</svg>
"""


def generate_rune_svg(key, name, desc, c1, c2, emoji):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <linearGradient id="rune_bg_{key}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#111827" />
      <stop offset="100%" stop-color="#1f2937" />
    </linearGradient>
  </defs>

  <rect width="200" height="200" rx="14" fill="url(#rune_bg_{key})" />
  <rect x="8" y="8" width="184" height="184" rx="10" fill="none" stroke="{c1}" stroke-width="3" />
  
  <!-- Rune Hexagon -->
  <polygon points="100,30 150,58 150,116 100,144 50,116 50,58" fill="{c1}" fill-opacity="0.18" stroke="{c2}" stroke-width="2" />
  <text x="100" y="96" font-size="46" text-anchor="middle" dominant-baseline="middle">{emoji}</text>

  <rect x="20" y="152" width="160" height="24" rx="5" fill="#030712" stroke="{c2}" stroke-width="1.5" />
  <text x="100" y="168" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="800" font-size="11" fill="#ffffff" text-anchor="middle">{name}</text>
  <text x="100" y="190" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="600" font-size="8" fill="{c2}" text-anchor="middle">{desc}</text>
</svg>
"""


def generate_cover_svg():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%">
  <defs>
    <linearGradient id="sky_bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#090d16" />
      <stop offset="40%" stop-color="#1e1b4b" />
      <stop offset="75%" stop-color="#4338ca" />
      <stop offset="100%" stop-color="#7c3aed" />
    </linearGradient>
    <linearGradient id="neon_title" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="35%" stop-color="#ec4899" />
      <stop offset="70%" stop-color="#facc15" />
      <stop offset="100%" stop-color="#22c55e" />
    </linearGradient>
  </defs>

  <rect width="800" height="450" fill="url(#sky_bg)" />

  <!-- Retro Pixel Grid Skyline -->
  <g fill="#020617" opacity="0.8">
    <rect x="40" y="240" width="60" height="210" />
    <rect x="120" y="190" width="80" height="260" />
    <rect x="220" y="270" width="70" height="180" />
    <rect x="310" y="170" width="90" height="280" />
    <rect x="420" y="220" width="70" height="230" />
    <rect x="510" y="160" width="100" height="290" />
    <rect x="630" y="250" width="60" height="200" />
    <rect x="710" y="210" width="70" height="240" />
  </g>

  <!-- Windows Grid -->
  <g fill="#fde047" opacity="0.6">
    <rect x="140" y="210" width="10" height="10" />
    <rect x="170" y="240" width="10" height="10" />
    <rect x="330" y="190" width="12" height="12" />
    <rect x="360" y="230" width="12" height="12" />
    <rect x="530" y="180" width="12" height="12" />
    <rect x="570" y="220" width="12" height="12" />
    <rect x="730" y="230" width="10" height="10" />
  </g>

  <!-- Big Neon Moon -->
  <circle cx="680" cy="110" r="55" fill="#e0e7ff" opacity="0.9" />
  <circle cx="660" cy="95" r="45" fill="url(#sky_bg)" />

  <!-- Stars -->
  <g fill="#ffffff" opacity="0.8">
    <rect x="80" y="60" width="4" height="4" />
    <rect x="180" y="90" width="6" height="6" />
    <rect x="290" y="45" width="4" height="4" />
    <rect x="450" y="80" width="5" height="5" />
    <rect x="560" y="50" width="4" height="4" />
  </g>

  <!-- Main Game Banner -->
  <g transform="translate(400, 150)">
    <!-- Shadow -->
    <text x="4" y="4" font-family="-apple-system, BlinkMacSystemFont, 'Impact', sans-serif" font-weight="900" font-size="58" fill="#090d16" text-anchor="middle" letter-spacing="4">指 尖 像 素 城</text>
    <!-- Foreground -->
    <text x="0" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Impact', sans-serif" font-weight="900" font-size="58" fill="url(#neon_title)" text-anchor="middle" letter-spacing="4">指 尖 像 素 城</text>
  </g>

  <g transform="translate(400, 215)">
    <rect x="-180" y="-18" width="360" height="36" rx="8" fill="#090d16" stroke="#38bdf8" stroke-width="2.5" />
    <text x="0" y="6" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="16" fill="#38bdf8" text-anchor="middle" letter-spacing="2">PIXEL CITY · 放置卡牌策略手游</text>
  </g>

  <!-- Features Badge Strip -->
  <g transform="translate(400, 275)">
    <rect x="-240" y="-14" width="480" height="28" rx="6" fill="#1e1b4b" opacity="0.9" stroke="#c084fc" stroke-width="1.5" />
    <text x="0" y="5" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="600" font-size="13" fill="#e0e7ff" text-anchor="middle">
      ⚡虚空神将 · 🌙怒气压制 · 🗡️破盾斩杀 · 🔮专属圣物
    </text>
  </g>
</svg>
"""


def main():
    print("Generating Pixel City SVG visual assets...")

    # 1. Heroes
    for key, name, role, c1, c2, c3, emoji in HEROES:
        p = os.path.join(HERO_DIR, f"{key}.svg")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(generate_hero_svg(key, name, role, c1, c2, c3, emoji))

    # 2. Relics
    for key, name, role, c1, c2, emoji in RELICS:
        p = os.path.join(RELIC_DIR, f"{key}.svg")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(generate_relic_svg(key, name, role, c1, c2, emoji))

    # 3. Runes
    for key, name, desc, c1, c2, emoji in RUNES:
        p = os.path.join(RUNE_DIR, f"{key}.svg")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(generate_rune_svg(key, name, desc, c1, c2, emoji))

    # 4. Covers
    cover_svg = generate_cover_svg()
    with open(os.path.join(HERO_DIR, "cover.svg"), 'w', encoding='utf-8') as f:
        f.write(cover_svg)
    with open(os.path.join(GAMES_DIR, "32.svg"), 'w', encoding='utf-8') as f:
        f.write(cover_svg)

    print(f"Successfully generated {len(HEROES)} heroes, {len(RELICS)} relics, {len(RUNES)} runes, and covers.")


if __name__ == '__main__':
    main()
