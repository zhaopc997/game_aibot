import { useParams, Link } from 'react-router-dom'
import { Heart, Bookmark, Share2, ChevronLeft, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Tag } from '@/components/ui/Tag'
import { Card, CardBody } from '@/components/ui/Card'

export default function GuideDetailPage() {
  useParams() // 未来真实接口用,目前数据为 mock
  return (
    <article className="pt-8 pb-20 max-w-3xl mx-auto">
      <Link to="/guides" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 返回攻略库
      </Link>

      <header className="mb-8">
        <div className="flex items-center gap-2 mb-3">
          <Tag>配装</Tag>
          <span className="text-sm text-ink-500">原神</span>
          <span className="text-ink-100">·</span>
          <span className="text-sm text-ink-500">v4.2</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-display font-semibold text-ink-900 leading-tight">
          4.2 钟离圣遗物毕业指南:从入门到精通
        </h1>
        <p className="mt-3 text-ink-500">2026-09-01 · 作者:攻略编辑组 · 阅读 12.3k</p>
      </header>

      <div className="flex items-center gap-2 mb-10">
        <Button variant="primary" size="sm"><Heart size={14} /> 点赞 (234)</Button>
        <Button variant="outline" size="sm"><Bookmark size={14} /> 收藏</Button>
        <Button variant="ghost" size="sm"><Share2 size={14} /> 分享</Button>
        <Link to="/ai" className="ml-auto">
          <Button variant="soft" size="sm"><Sparkles size={14} /> AI 总结</Button>
        </Link>
      </div>

      <div className="prose-article">
        <h2>前言</h2>
        <p>钟离作为原神的"岩王帝君",在 4.2 版本中依旧是顶级辅助角色。本文将系统讲解钟离的圣遗物选择、词条优先级与配队方案,帮你从入门到精通。</p>

        <h3>一、圣遗物选择</h3>
        <p>推荐 <code>悠古的磐岩</code> 4 件套,提供 35% 岩元素伤害加成,完美契合钟离的辅助定位。</p>
        <blockquote>开箱优先级:生之花 &gt; 死之羽 &gt; 时之沙 &gt; 空之杯 &gt; 理之冠</blockquote>

        <h3>二、词条优先级</h3>
        <p>主词条选择:充能沙 &gt; 岩伤杯 &gt; 暴击头。<br />
        副词条优先级:暴击率 &gt; 暴击伤害 &gt; 充能效率 &gt; 生命值。</p>

        <pre>{`圣遗物评分公式:
  score = crit_rate * 2 + crit_dmg + recharge * 0.5
  ≥ 200 毕业 / 150-200 优秀 / 100-150 良好`}</pre>

        <h2>三、配队方案</h2>
        <p>钟离的配队非常灵活,以下是 4.2 版本最强配队:</p>
        <ul>
          <li><strong>双岩共鸣</strong>:钟离 + 任意岩 + 双火/双水</li>
          <li><strong>万能辅助</strong>:钟离 + 主C + 副C + 奶妈</li>
        </ul>

        <h2>总结</h2>
        <p>钟离的培养门槛低、上限高,是所有玩家都值得练的角色。合理配装后,你会发现游戏体验提升一个档次。</p>
      </div>

      <Card className="mt-12">
        <CardBody>
          <h3 className="text-lg font-display font-semibold text-ink-900 mb-3 flex items-center gap-2">
            <Sparkles size={18} className="text-accent-500" /> AI 助手推荐
          </h3>
          <p className="text-sm text-ink-500 mb-4">想看更多当前版本的角色配装?问问 AI 助手。</p>
          <Link to="/ai">
            <Button variant="primary" size="sm">问问 AI →</Button>
          </Link>
        </CardBody>
      </Card>
    </article>
  )
}
