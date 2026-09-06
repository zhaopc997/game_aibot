import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import GameListPage from './pages/GameListPage'
import GameDetailPage from './pages/GameDetailPage'
import GuideListPage from './pages/GuideListPage'
import GuideDetailPage from './pages/GuideDetailPage'
import GuideEditorPage from './pages/GuideEditorPage'
import AIChatPage from './pages/AIChatPage'
import MapViewerPage from './pages/MapViewerPage'
import SimulatorPage from './pages/SimulatorPage'
import QAPage from './pages/QAPage'
import NotificationsPage from './pages/NotificationsPage'
import AdminPage from './pages/AdminPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import OAuthCallbackPage from './pages/OAuthCallbackPage'

export default function App() {
  const { token } = useAuth()

  return (
    <Routes>
      {/* 公开页(无顶栏) */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/oauth/callback" element={<OAuthCallbackPage />} />

      {/* 业务页(顶栏布局) */}
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/games" element={<GameListPage />} />
        <Route path="/games/:id" element={<GameDetailPage />} />
        <Route path="/games/:id/maps" element={<MapViewerPage />} />
        <Route path="/games/:id/simulators" element={<SimulatorPage />} />
        <Route path="/guides" element={<GuideListPage />} />
        <Route path="/guides/:id" element={<GuideDetailPage />} />
        <Route
          path="/guides/new"
          element={token ? <GuideEditorPage /> : <Navigate to="/login" replace />}
        />
        <Route path="/ai" element={<AIChatPage />} />
        <Route path="/qa" element={<QAPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route
          path="/profile"
          element={token ? <ProfilePage /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/admin"
          element={token ? <AdminPage /> : <Navigate to="/login" replace />}
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
