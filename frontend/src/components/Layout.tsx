import { Link, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Layout() {
  const { token, user, logout } = useAuth()
  const navigate = useNavigate()
  const isAdmin = user?.roles?.includes('ADMIN')

  return (
    <>
      <nav className="navbar">
        <div className="container">
          <Link to="/" className="brand">游戏攻略平台</Link>
          <Link to="/">攻略</Link>
          <Link to="/qa">问答</Link>
          <Link to="/notifications">通知</Link>
          {isAdmin && <Link to="/admin">管理后台</Link>}
          <span className="spacer" />
          {token ? (
            <>
              <Link to="/profile">{user?.username || '个人中心'}</Link>
              <button className="btn" onClick={() => { logout(); navigate('/') }}>退出</button>
            </>
          ) : (
            <Link to="/login" className="btn">登录</Link>
          )}
        </div>
      </nav>
      <div className="container">
        <Outlet />
      </div>
    </>
  )
}
