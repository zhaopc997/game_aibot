import { Bell } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'

const NOTIFS = [
  { id: 1, type: 'guide',   title: '你关注的攻略有更新', desc: '《4.2 钟离圣遗物毕业指南》已更新到 v4.2.1', time: '10 分钟前' },
  { id: 2, type: 'version', title: '原神 4.2.1 补丁上线',  desc: '新增 2 个 Boss,调整了部分角色平衡', time: '2 小时前' },
  { id: 3, type: 'qa',      title: '你的问题被采纳',         desc: '《钟离值不值得抽》被选为最佳答案',     time: '1 天前' },
]

export default function NotificationsPage() {
  return (
    <div className="pt-10 pb-20 max-w-2xl mx-auto">
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-6">通知</h1>
      <Card>
        <CardBody className="p-0">
          {NOTIFS.map((n, i) => (
            <div
              key={n.id}
              className={`flex items-start gap-4 p-5 ${i < NOTIFS.length - 1 ? 'border-b border-ink-100' : ''}`}
            >
              <div className="h-10 w-10 rounded-2xl bg-accent-50 text-accent-500 grid place-items-center shrink-0">
                <Bell size={16} />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-ink-900">{n.title}</h3>
                <p className="mt-1 text-sm text-ink-500">{n.desc}</p>
                <p className="mt-1.5 text-xs text-ink-300">{n.time}</p>
              </div>
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  )
}
