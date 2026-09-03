import { useAuth } from '../auth/AuthContext'

export default function Profile() {
  const { user } = useAuth()

  if (!user) return <p className="muted">未登录</p>

  return (
    <div className="card" style={{ maxWidth: 560 }}>
      <h2 style={{ marginTop: 0 }}>个人中心</h2>
      <p><b>用户名：</b>{user.username}</p>
      <p><b>邮箱：</b>{user.email}</p>
      <p><b>等级：</b>Lv.{user.level}（经验 {user.exp}）</p>
      <p><b>角色：</b>{user.roles.join(' / ') || 'USER'}</p>
      {user.bio && <p><b>简介：</b>{user.bio}</p>}
    </div>
  )
}
