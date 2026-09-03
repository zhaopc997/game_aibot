import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'
import Layout from './components/Layout'
import GuideList from './pages/GuideList'
import GuideDetail from './pages/GuideDetail'
import GuideEditor from './pages/GuideEditor'
import GameDetail from './pages/GameDetail'
import MapViewer from './pages/MapViewer'
import SimulatorPage from './pages/SimulatorPage'
import QA from './pages/QA'
import Notifications from './pages/Notifications'
import Admin from './pages/Admin'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import OAuthCallback from './pages/OAuthCallback'

export default function App() {
  const { token } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/oauth/callback" element={<OAuthCallback />} />
      <Route element={<Layout />}>
        <Route path="/" element={<GuideList />} />
        <Route path="/guides/:id" element={<GuideDetail />} />
        <Route path="/guides/new" element={token ? <GuideEditor /> : <Navigate to="/login" replace />} />
        <Route path="/games/:id" element={<GameDetail />} />
        <Route path="/games/:id/maps" element={<MapViewer />} />
        <Route path="/games/:id/simulators" element={<SimulatorPage />} />
        <Route path="/qa" element={<QA />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/admin" element={token ? <Admin /> : <Navigate to="/login" replace />} />
        <Route path="/profile" element={token ? <Profile /> : <Navigate to="/login" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
