import { Link } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardBody } from '@/components/ui/Card'

export default function GuideEditorPage() {
  const [title, setTitle] = useState('')
  return (
    <div className="pt-8 pb-20 max-w-3xl mx-auto">
      <Link to="/guides" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 取消
      </Link>
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-6">写新攻略</h1>

      <Card>
        <CardBody className="space-y-4">
          <div>
            <label className="text-sm text-ink-700 mb-1.5 block">标题</label>
            <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="给你的攻略起个标题…" />
          </div>
          <div>
            <label className="text-sm text-ink-700 mb-1.5 block">内容</label>
            <textarea
              rows={12}
              placeholder="支持 Markdown 语法…"
              className="w-full px-4 py-3 text-sm rounded-2xl bg-canvas border border-ink-100 placeholder:text-ink-300 focus:outline-none focus:border-accent-500 focus:shadow-glow transition-all resize-y"
            />
          </div>
          <div className="flex items-center justify-end gap-2">
            <Button variant="ghost">保存草稿</Button>
            <Button variant="primary">提交审核</Button>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
