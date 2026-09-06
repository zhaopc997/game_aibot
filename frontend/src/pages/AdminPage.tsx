import { Settings, Users, FileText, ShieldCheck } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'

const SECTIONS = [
  { icon: FileText,  title: '内容审核', desc: '12 篇待审核', color: 'text-accent-700' },
  { icon: Users,     title: '用户管理', desc: '348 位注册用户', color: 'text-accent-700' },
  { icon: ShieldCheck, title: '系统设置', desc: 'AI 工具、限流、通知', color: 'text-accent-700' },
  { icon: Settings,  title: '运营配置', desc: 'Banner、活动、版本', color: 'text-accent-700' },
]

export default function AdminPage() {
  return (
    <div className="pt-10 pb-20">
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-2">管理后台</h1>
      <p className="text-sm text-ink-500 mb-8">仅管理员可见</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {SECTIONS.map((s) => {
          const Icon = s.icon
          return (
            <Card key={s.title} className="hover:shadow-lift transition-shadow cursor-pointer">
              <CardBody className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-2xl bg-accent-50 grid place-items-center">
                  <Icon size={20} className="text-accent-500" />
                </div>
                <div>
                  <h3 className="text-base font-medium text-ink-900">{s.title}</h3>
                  <p className="text-sm text-ink-500">{s.desc}</p>
                </div>
              </CardBody>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
