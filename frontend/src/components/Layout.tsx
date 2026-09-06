import { Outlet } from 'react-router-dom'
import TopNav from './TopNav'

/**
 * 全站布局 —— 顶部水平导航 + 主体 + 极简 footer。
 * 整体留白大,信息密度低,符合日式极简风。
 */
export default function Layout() {
  return (
    <div className="min-h-full flex flex-col">
      <TopNav />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-ink-100/60 mt-24 py-10">
        <div className="container flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-ink-500">
          <span className="font-display">© 2026 game_aibot · 游戏智能平台</span>
          <div className="flex items-center gap-5">
            <a className="hover:text-ink-700 transition-colors" href="#">关于</a>
            <a className="hover:text-ink-700 transition-colors" href="#">条款</a>
            <a className="hover:text-ink-700 transition-colors" href="#">隐私</a>
            <a className="hover:text-ink-700 transition-colors" href="#">联系</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
