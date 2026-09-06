import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, MapPin } from 'lucide-react'
import { Card } from '@/components/ui/Card'

export default function MapViewerPage() {
  useParams()
  return (
    <div className="pt-8 pb-20">
      <Link to="/games" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 返回游戏
      </Link>
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-6">互动地图</h1>
      <Card className="p-10 text-center bg-canvas">
        <MapPin size={40} className="mx-auto text-accent-300 mb-3" />
        <p className="text-ink-500">V2 阶段将接入 Canvas 渲染的真实游戏地图</p>
        <p className="text-xs text-ink-300 mt-1">数据加载中…</p>
      </Card>
    </div>
  )
}
