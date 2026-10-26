import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, Save, Bot, Gauge, Bell } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

/** 系统设置：前端演示表单（真实后端配置项可按需扩展） */
export default function SettingsAdminPage() {
  const [aiModel, setAiModel] = useState('gpt-4o-mini')
  const [rateLimit, setRateLimit] = useState('60')
  const [notifyEnabled, setNotifyEnabled] = useState(true)
  const [saved, setSaved] = useState(false)

  function save() {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="pt-10 pb-20 max-w-2xl">
      <Link to="/admin" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-4">
        <ChevronLeft size={14} /> 返回管理后台
      </Link>
      <h1 className="text-2xl font-display font-semibold text-ink-900 mb-6">系统设置</h1>

      <Card className="mb-4">
        <CardBody>
          <h3 className="flex items-center gap-2 text-base font-medium text-ink-900 mb-4"><Bot size={16} className="text-accent-500" /> AI 工具</h3>
          <label className="text-sm text-ink-600 mb-1 block">默认模型</label>
          <Input value={aiModel} onChange={(e) => setAiModel(e.target.value)} className="max-w-xs" />
        </CardBody>
      </Card>

      <Card className="mb-4">
        <CardBody>
          <h3 className="flex items-center gap-2 text-base font-medium text-ink-900 mb-4"><Gauge size={16} className="text-accent-500" /> 限流</h3>
          <label className="text-sm text-ink-600 mb-1 block">每分钟请求上限</label>
          <Input value={rateLimit} onChange={(e) => setRateLimit(e.target.value)} className="max-w-xs" type="number" />
        </CardBody>
      </Card>

      <Card className="mb-4">
        <CardBody>
          <h3 className="flex items-center gap-2 text-base font-medium text-ink-900 mb-4"><Bell size={16} className="text-accent-500" /> 通知</h3>
          <label className="flex items-center gap-2 text-sm text-ink-700 cursor-pointer">
            <input type="checkbox" checked={notifyEnabled} onChange={(e) => setNotifyEnabled(e.target.checked)} />
            启用站内通知推送
          </label>
        </CardBody>
      </Card>

      <div className="flex items-center gap-3">
        <Button onClick={save}><Save size={15} /> 保存设置</Button>
        {saved && <span className="text-sm text-accent-700">已保存</span>}
      </div>
    </div>
  )
}
