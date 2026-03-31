import { useAuth } from '@/hooks/useAuth'
import LoginPage from '@/pages/LoginPage'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppShell from '@/components/layout/AppShell'
import DashboardPage from '@/pages/DashboardPage'
import WorkoutsPage from '@/pages/WorkoutsPage'
import ExercisesPage from '@/pages/ExercisesPage'

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-foreground" />
      </div>
    )
  }

  if (!user) return <LoginPage />

  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/workouts" element={<WorkoutsPage />} />
          <Route path="/exercises" element={<ExercisesPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}

export default App
