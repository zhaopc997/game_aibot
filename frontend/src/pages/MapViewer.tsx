import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import client, { unwrap } from '../api/client'
import { useAuth } from '../auth/AuthContext'

interface Marker {
  id?: string
  x: number
  y: number
  label?: string
  color?: string
}

interface MapData {
  id: number
  name: string
  mapImageUrl?: string
  markers: Marker[]
}

export default function MapViewer() {
  const { id } = useParams()
  const { token } = useAuth()
  const [map, setMap] = useState<MapData | null>(null)
  const [marker, setMarker] = useState<Marker | null>(null)
  const [label, setLabel] = useState('')

  useEffect(() => {
    client.get(`/tools/maps/${id}`).then((r) => setMap(unwrap<MapData>(r)))
  }, [id])

  function onCanvasClick(e: React.MouseEvent<HTMLDivElement>) {
    if (!token) return
    const rect = e.currentTarget.getBoundingClientRect()
    const x = Math.round(((e.clientX - rect.left) / rect.width) * 10000) / 100
    const y = Math.round(((e.clientY - rect.top) / rect.height) * 10000) / 100
    setMarker({ x, y, label: '' })
  }

  async function addMarker() {
    if (!map || !marker) return
    const body = { ...marker, label: label || '标记点' }
    const r = await client.post(`/tools/maps/${map.id}/markers`, body)
    setMap(unwrap<MapData>(r)); setMarker(null); setLabel('')
  }

  async function removeMarker(markerId: string) {
    if (!map) return
    const r = await client.delete(`/tools/maps/${map.id}/markers/${markerId}`)
    setMap(unwrap<MapData>(r))
  }

  return (
    <div style={{ maxWidth: 900 }}>
      <h2>{map?.name || '互动地图'}</h2>
      {!map && <p className="muted">加载中…</p>}
      {map && (
        <>
          <div
            style={{ position: 'relative', cursor: token ? 'crosshair' : 'default', marginBottom: 12 }}
            onClick={onCanvasClick}
          >
            <img
              src={map.mapImageUrl || 'https://placehold.co/900x500?text=Map'}
              alt={map.name}
              style={{ width: '100%', display: 'block', borderRadius: 10 }}
            />
            {map.markers.map((m) => (
              <div
                key={m.id}
                onClick={(e) => { e.stopPropagation(); m.id && removeMarker(m.id) }}
                title={m.label}
                style={{
                  position: 'absolute', left: `${m.x}%`, top: `${m.y}%`,
                  transform: 'translate(-50%, -100%)', cursor: 'pointer',
                }}
              >
                <span style={{ color: m.color || '#ef4444', fontSize: 22 }}>📍</span>
              </div>
            ))}
            {marker && (
              <div style={{ position: 'absolute', left: `${marker.x}%`, top: `${marker.y}%`, transform: 'translate(-50%, -100%)' }}>
                <span style={{ fontSize: 22 }}>📍</span>
              </div>
            )}
          </div>

          {token && marker && (
            <div style={{ display: 'flex', gap: 8 }}>
              <input className="input" placeholder="标记名称" value={label}
                     onChange={(e) => setLabel(e.target.value)} style={{ marginBottom: 0 }} />
              <button className="btn btn-primary" onClick={addMarker}>添加标记</button>
            </div>
          )}
          {!token && <p className="muted">登录后可添加标记，点击地图放置</p>}
        </>
      )}
    </div>
  )
}
