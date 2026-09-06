import { useAuth } from '@/auth/AuthContext'
import { Avatar } from '@/components/ui/Avatar'
import { Card, CardBody } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'

export default function ProfilePage() {
  const { user } = useAuth()
  return (
    <div className="pt-10 pb-20 max-w-2xl mx-auto">
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-6">个人中心</h1>
      <Card>
        <CardBody className="flex items-center gap-5">
          <Avatar size="lg" rounded="3xl">
            {user?.username?.[0]?.toUpperCase() ?? 'U'}
          </Avatar>
          <div>
            <h2 className="text-xl font-medium text-ink-900">{user?.username}</h2>
            <p className="text-sm text-ink-500 mt-1">{user?.email ?? '未设置邮箱'}</p>
            <div className="mt-3 flex items-center gap-1.5">
              {user?.roles?.map((r) => <Tag key={r}>{r}</Tag>) ?? <Tag variant="outline">USER</Tag>}
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
