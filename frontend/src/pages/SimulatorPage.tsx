import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, Calculator } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

export default function SimulatorPage() {
  useParams()
  return (
    <div className="pt-8 pb-20">
      <Link to="/games" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 返回游戏
      </Link>
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-6">Build 模拟器</h1>
      <Card>
        <CardBody className="text-center py-16">
          <Calculator size={40} className="mx-auto text-accent-300 mb-3" />
          <p className="text-ink-500">角色、装备、词条自由组合,实时计算伤害</p>
          <Button variant="primary" className="mt-6">开始搭配</Button>
        </CardBody>
      </Card>
    </div>
  )
}
