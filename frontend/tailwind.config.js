/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    container: {
      center: true,
      padding: '1.5rem',
      screens: { '2xl': '1280px' },
    },
    extend: {
      colors: {
        // 强调色:珊瑚红(暖橙),可在 tailwind.config 一键改整套
        accent: {
          50:  '#FFF4F0',
          100: '#FFE2D5',
          200: '#FFBFAA',
          300: '#FF9873',
          400: '#FF8057',
          500: '#FF6B47',
          600: '#E55533',
          700: '#BF4327',
          800: '#8F321D',
          900: '#5F2213',
        },
        // 中性背景
        canvas:   '#FAF8F5',   // 页面底色(米白)
        surface:  '#FFFFFF',   // 卡片
        elevated: '#FFFFFF',   // 悬浮卡片
        // 中性文字
        ink: {
          900: '#1A1A1A',  // 标题
          700: '#3A3A3A',  // 正文
          500: '#6B6B6B',  // 次要
          300: '#B5B5B5',  // 禁用/占位
          100: '#E8E5DF',  // 分隔线
        },
      },
      fontFamily: {
        sans:    ['Inter', '"PingFang SC"', 'system-ui', 'sans-serif'],
        display: ['"Source Han Serif SC"', '"Noto Serif SC"', 'ui-serif', 'serif'],
      },
      borderRadius: {
        'xl':   '0.875rem',   // 14px
        '2xl':  '1.25rem',    // 20px 标准卡
        '3xl':  '1.75rem',    // 28px 大卡
        '4xl':  '2.5rem',     // 40px hero
      },
      boxShadow: {
        'soft': '0 1px 2px rgba(26,26,26,0.04), 0 4px 16px rgba(26,26,26,0.04)',
        'lift': '0 2px 4px rgba(26,26,26,0.05), 0 12px 32px rgba(26,26,26,0.08)',
        'glow': '0 0 0 4px rgba(255,107,71,0.18)',
      },
      transitionTimingFunction: {
        'soft': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
