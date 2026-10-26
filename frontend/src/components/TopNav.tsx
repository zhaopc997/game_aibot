import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  Search, Bell, Sparkles, User, LogOut, ChevronDown, Gamepad2, Menu, X,
} from 'lucide-react'
import { useAuth } from '@/auth/AuthContext'
import { cn } from '@/lib/utils'
import { Button, IconButton } from '@/components/ui/Button'
import { Avatar } from '@/components/ui/Avatar'

/** 顶部水平导航条 —— 桌面端水平导航 / 移动端抽屉 */
export default function TopNav() {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()
  const isAdmin = user?.roles?.includes('ADMIN')
  const [menuOpen, setMenuOpen] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [drawerSearch, setDrawerSearch] = useState('')

  const navItems = [
    { label: '游戏库', to: '/games' },
    { label: '攻略',   to: '/guides' },
    { label: '社区',   to: '/qa' },
    { label: 'AI 助手', to: '/ai', icon: Sparkles },
  ]

  function submitSearch(value: string) {
    const v = value.trim()
    if (!v) return
    setDrawerOpen(false)
    navigate(`/games?q=${encodeURIComponent(v)}`)
  }

  return (
    <header className="sticky top-0 z-40 bg-canvas/85 backdrop-blur-md border-b border-ink-100/60">
      <div className="container flex items-center gap-6 h-16">
        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-2 group shrink-0"
        >
          <span className="grid place-items-center h-9 w-9 rounded-2xl bg-accent-500 text-white shadow-soft transition-transform duration-200 group-hover:scale-105">
            <Gamepad2 size={18} strokeWidth={2.4} />
          </span>
          <span className="text-lg font-display font-semibold tracking-wide text-ink-900">
            game_aibot
          </span>
        </Link>

        {/* 移动端汉堡按钮(<768px 唯一的导航入口) */}
        <IconButton
          className="md:hidden ml-auto"
          aria-label={drawerOpen ? '关闭菜单' : '打开菜单'}
          aria-expanded={drawerOpen}
          onClick={() => setDrawerOpen((v) => !v)}
        >
          {drawerOpen ? <X size={20} strokeWidth={2.2} /> : <Menu size={20} strokeWidth={2.2} />}
        </IconButton>

        {/* 一级导航 */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((it) => {
            const Icon = it.icon
            return (
              <Link
                key={it.to}
                to={it.to}
                className={cn(
                  'group inline-flex items-center gap-1.5 px-3.5 h-10 rounded-xl',
                  'text-sm font-medium text-ink-700',
                  'transition-all duration-200 ease-soft',
                  'hover:bg-accent-50 hover:text-accent-700'
                )}
              >
                {Icon && <Icon size={15} strokeWidth={2.2} />}
                {it.label}
              </Link>
            )
          })}
          {isAdmin && (
            <Link
              to="/admin"
              className="px-3.5 h-10 inline-flex items-center text-sm font-medium text-ink-700 rounded-xl hover:bg-accent-50 hover:text-accent-700 transition-colors"
            >
              管理
            </Link>
          )}
        </nav>

        {/* 搜索框(居中扩) */}
        <div className="hidden lg:block flex-1 max-w-md">
          <div className="relative">
            <Search
              size={16}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-300 pointer-events-none"
            />
            <input
              type="search"
              placeholder="搜索游戏、攻略、问答…"
              className="h-10 w-full pl-10 pr-4 text-sm rounded-xl bg-surface border border-ink-100 text-ink-900 placeholder:text-ink-300 focus:outline-none focus:border-accent-500 focus:shadow-glow transition-all"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  submitSearch((e.target as HTMLInputElement).value)
                }
              }}
            />
          </div>
        </div>

        {/* 右侧操作 */}
        <div className="hidden md:flex items-center gap-1.5 ml-auto">
          {token ? (
            <>
              <IconButton aria-label="通知" onClick={() => navigate('/notifications')}>
                <Bell size={18} strokeWidth={2.2} />
              </IconButton>
              {/* 用户菜单 */}
              <div className="relative">
                <button
                  onClick={() => setMenuOpen((v) => !v)}
                  onBlur={() => setTimeout(() => setMenuOpen(false), 150)}
                  className="flex items-center gap-1.5 h-10 pl-1.5 pr-2 rounded-xl hover:bg-ink-100 transition-colors"
                >
                  <Avatar size="sm" rounded="2xl">
                    {user?.username?.[0]?.toUpperCase() ?? 'U'}
                  </Avatar>
                  <ChevronDown size={14} className="text-ink-500" />
                </button>
                {menuOpen && (
                  <div className="absolute right-0 top-12 w-48 bg-surface rounded-2xl shadow-lift border border-ink-100 p-1.5 animate-in fade-in slide-in-from-top-2">
                    <button
                      onMouseDown={(e) => { e.preventDefault(); navigate('/profile'); setMenuOpen(false) }}
                      className="w-full flex items-center gap-2 px-3 h-9 rounded-xl text-sm text-ink-700 hover:bg-ink-100"
                    >
                      <User size={14} /> 个人中心
                    </button>
                    <button
                      onMouseDown={(e) => { e.preventDefault(); logout(); navigate('/'); setMenuOpen(false) }}
                      className="w-full flex items-center gap-2 px-3 h-9 rounded-xl text-sm text-accent-700 hover:bg-accent-50"
                    >
                      <LogOut size={14} /> 退出登录
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost" size="sm">登录</Button>
              </Link>
              <Link to="/register">
                <Button variant="primary" size="sm">注册</Button>
              </Link>
            </>
          )}
        </div>
      </div>

      {/* 移动端抽屉导航：挂在 header 内用绝对定位，天然与导航栏对齐，
          不依赖 h-18/top-18（h-18 未在 tailwind.config 定义，导航栏高度非固定值） */}
      {drawerOpen && (
        <>
          <div
            className="md:hidden fixed inset-0 z-40 bg-ink-900/40"
            onClick={() => setDrawerOpen(false)}
          />
          <nav className="md:hidden absolute left-0 right-0 top-full z-50 bg-canvas border-b border-ink-100 shadow-lift px-4 py-4 flex flex-col gap-1 max-h-[calc(100vh-4rem)] overflow-y-auto animate-in fade-in slide-in-from-top-2">
            <div className="relative mb-2">
              <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-300 pointer-events-none" />
              <input
                type="search"
                value={drawerSearch}
                onChange={(e) => setDrawerSearch(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') submitSearch(drawerSearch) }}
                placeholder="搜索游戏、攻略、问答…"
                className="h-11 w-full pl-10 pr-4 text-sm rounded-xl bg-surface border border-ink-100 text-ink-900 placeholder:text-ink-300 focus:outline-none focus:border-accent-500"
              />
            </div>
            {navItems.map((it) => {
              const Icon = it.icon
              return (
                <Link
                  key={it.to}
                  to={it.to}
                  onClick={() => setDrawerOpen(false)}
                  className="flex items-center gap-2 px-3 h-11 rounded-xl text-sm font-medium text-ink-700 hover:bg-accent-50 hover:text-accent-700"
                >
                  {Icon && <Icon size={16} strokeWidth={2.2} />}
                  {it.label}
                </Link>
              )
            })}
            {isAdmin && (
              <Link
                to="/admin"
                onClick={() => setDrawerOpen(false)}
                className="flex items-center gap-2 px-3 h-11 rounded-xl text-sm font-medium text-ink-700 hover:bg-accent-50 hover:text-accent-700"
              >
                管理
              </Link>
            )}
            <div className="my-2 border-t border-ink-100" />
            {token ? (
              <>
                <Link
                  to="/notifications"
                  onClick={() => setDrawerOpen(false)}
                  className="flex items-center gap-2 px-3 h-11 rounded-xl text-sm text-ink-700 hover:bg-ink-100"
                >
                  <Bell size={16} /> 通知
                </Link>
                <Link
                  to="/profile"
                  onClick={() => setDrawerOpen(false)}
                  className="flex items-center gap-2 px-3 h-11 rounded-xl text-sm text-ink-700 hover:bg-ink-100"
                >
                  <User size={16} /> 个人中心
                </Link>
                <button
                  onClick={() => { setDrawerOpen(false); logout(); navigate('/') }}
                  className="flex items-center gap-2 px-3 h-11 rounded-xl text-sm text-accent-700 hover:bg-accent-50"
                >
                  <LogOut size={16} /> 退出登录
                </button>
              </>
            ) : (
              <div className="flex gap-2 px-1">
                <Link to="/login" onClick={() => setDrawerOpen(false)} className="flex-1">
                  <Button variant="outline" size="sm" className="w-full">登录</Button>
                </Link>
                <Link to="/register" onClick={() => setDrawerOpen(false)} className="flex-1">
                  <Button variant="primary" size="sm" className="w-full">注册</Button>
                </Link>
              </div>
            )}
          </nav>
        </>
      )}
    </header>
  )
}
