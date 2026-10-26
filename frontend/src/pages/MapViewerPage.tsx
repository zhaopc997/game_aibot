import { useCallback, useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, MapPin } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import client, { unwrap } from '@/api/client'

interface Marker {
  marker_id?: number | string
  name?: string
  /** 归一化坐标(0-100)，与后端 markers jsonb 中的 coord_x/coord_y 对应 */
  coord_x?: number
  coord_y?: number
  [k: string]: unknown
}

interface InteractiveMap {
  id: number
  gameId: number
  name: string
  mapImageUrl?: string | null
  markers?: Marker[]
}

export default function MapViewerPage() {
  const { id } = useParams<{ id: string }>()
  const [maps, setMaps] = useState<InteractiveMap[]>([])
  const [activeId, setActiveId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  /** 底图加载失败标记：声明式降级，避免用 style.display 手动隐藏 img */
  const [mapImgFailed, setMapImgFailed] = useState(false)

  const gameId = Number(id)

  const load = useCallback(() => {
    if (!Number.isFinite(gameId) || gameId <= 0) {
      setError('缺少有效的游戏 ID')
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    setMapImgFailed(false)
    client
      .get(`/tools/maps?gameId=${gameId}`)
      .then((r) => {
        const data = unwrap<InteractiveMap[]>(r) ?? []
        setMaps(data)
        setActiveId(data.length > 0 ? data[0].id : null)
      })
      .catch((e: unknown) => {
        const err = e as { message?: string }
        setError(err.message ?? '加载地图失败，请稍后重试')
        setMaps([])
      })
      .finally(() => setLoading(false))
  }, [gameId])

  /** 标记点列表（底图加载失败时降级展示，避免标记信息一起丢失） */
  function renderMarkers(map: InteractiveMap) {
    const list = map.markers ?? []
    if (list.length === 0) return null
    return (
      <ul className="mt-3 space-y-2 text-left">
        {list.map((mk, i) => (
          <li key={String(mk.marker_id ?? i)} className="flex items-start gap-2 text-sm">
            <MapPin size={14} className="text-accent-500 mt-0.5 shrink-0" />
            <span className="text-ink-700">{mk.name ?? `标记 ${i + 1}`}</span>
          </li>
        ))}
      </ul>
    )
  }

  useEffect(load, [load])

  const active = maps.find((m) => m.id === activeId) ?? null

  return (
    <div className="pt-8 pb-20">
      <Link to={`/games/${gameId}`} className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 返回游戏
      </Link>
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-6">互动地图</h1>

      {loading ? (
        <p className="text-ink-500 text-center py-12">加载中…</p>
      ) : error ? (
        <p className="text-danger-600 text-center py-12">{error}</p>
      ) : maps.length === 0 ? (
        <Card className="p-10 text-center bg-canvas">
          <MapPin size={40} className="mx-auto text-accent-300 mb-3" />
          <p className="text-ink-500">该游戏暂未上传互动地图</p>
          <p className="text-xs text-ink-300 mt-1">地图数据由运营在后台维护</p>
        </Card>
      ) : (
        <>
          {maps.length > 1 && (
            <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin mb-6">
              {maps.map((m) => (
                <button
                  key={m.id}
                  onClick={() => { setActiveId(m.id); setMapImgFailed(false) }}
                  className={`shrink-0 h-9 px-3.5 rounded-xl text-sm font-medium transition-all ${
                    activeId === m.id
                      ? 'bg-accent-500 text-white'
                      : 'bg-surface text-ink-700 border border-ink-100 hover:border-ink-300'
                  }`}
                >{m.name}</button>
              ))}
            </div>
          )}

          {active && (
            <Card className="overflow-hidden">
              <CardBody className="p-0">
                {active.mapImageUrl ? (
                  !mapImgFailed ? (
                    <div className="relative w-full bg-canvas">
                      <img
                        src={active.mapImageUrl}
                        alt={active.name}
                        className="w-full block"
                        // 用 state 声明式降级，而非 style.display='none'：
                        // 后者绕过 React，组件卸载时会抛 removeChild 异常导致白屏
                        onError={() => setMapImgFailed(true)}
                      />
                      {/* 标记点叠加层：按归一化坐标绝对定位 */}
                      {(active.markers ?? []).map((mk, i) => {
                        const x = Number(mk.coord_x)
                        const y = Number(mk.coord_y)
                        if (!Number.isFinite(x) || !Number.isFinite(y)) return null
                        return (
                          <span
                            key={String(mk.marker_id ?? i)}
                            title={mk.name ?? `标记 ${i + 1}`}
                            className="absolute -translate-x-1/2 -translate-y-1/2"
                            style={{ left: `${x}%`, top: `${y}%` }}
                          >
                            <MapPin size={20} className="text-accent-500 drop-shadow" fill="currentColor" />
                          </span>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="p-10 text-center bg-canvas">
                      <MapPin size={40} className="mx-auto text-accent-300 mb-3" />
                      <p className="text-ink-500">{active.name} 底图加载失败</p>
                      {renderMarkers(active)}
                    </div>
                  )
                ) : (
                  <div className="p-10 text-center bg-canvas">
                    <MapPin size={40} className="mx-auto text-accent-300 mb-3" />
                    <p className="text-ink-500">{active.name} 暂无底图</p>
                  </div>
                )}

                {(active.markers ?? []).length > 0 && (
                  <div className="p-5 border-t border-ink-100">
                    <h2 className="text-sm font-medium text-ink-900 mb-3">
                      标记点（{active.markers!.length}）
                    </h2>
                    <ul className="space-y-2">
                      {active.markers!.map((mk, i) => (
                        <li key={String(mk.marker_id ?? i)} className="flex items-start gap-2 text-sm">
                          <MapPin size={14} className="text-accent-500 mt-0.5 shrink-0" />
                          <span className="text-ink-700">{mk.name ?? `标记 ${i + 1}`}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardBody>
            </Card>
          )}
        </>
      )}
    </div>
  )
}