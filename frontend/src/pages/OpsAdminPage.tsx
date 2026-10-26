import { Link } from 'react-router-dom'
import { ChevronLeft, Image, Calendar, Layers } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'

/** 运营配置：Banner / 活动 / 版本占位页 */
export default function OpsAdminPage() {
  return (
    <div className="pt-10 pb-20 max-w-2xl">
      <Link to="/admin" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-4">
        <ChevronLeft size={14} /> 返回管理后台
      </Link>
      <h1 className="text-2xl font-display font-semibold text-ink-900 mb-6">运营配置</h1>

      <Card className="mb-4">
        <CardBody>
          <h3 className="flex items-center gap-2 text-base font-medium text-ink-900 mb-1"><Image size={16} className="text-accent-500" /> Banner</h3>
          <p className="text-sm text-ink-500 mb-3">首页轮播图与运营位配置</p>
          <Tag size="sm">暂无 Banner</Tag>
        </CardBody>
      </Card>

      <Card className="mb-4">
        <CardBody>
          <h3 className="flex items-center gap-2 text-base font-medium text-ink-900 mb-1"><Calendar size={16} className="text-accent-500" /> 活动</h3>
          <p className="text-sm text-ink-500 mb-3">攻略大赛、签到等运营活动</p>
          <Tag size="sm">暂无活动</Tag>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <h3 className="flex items-center gap-2 text-base font-medium text-ink-900 mb-1"><Layers size={16} className="text-accent-500" /> 版本</h3>
          <p className="text-sm text-ink-500 mb-3">各游戏版本管理与发布节奏</p>
          <Tag size="sm">查看游戏库</Tag>
        </CardBody>
      </Card>
    </div>
  )
}
