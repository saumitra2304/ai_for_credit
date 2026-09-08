import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { TooltipProvider } from '@/components/ui/tooltip'
import { LeftSidebar } from '@/components/LeftSidebar'
import { ChatInterface } from '@/components/ChatInterface'
import { AdminPage } from '@/pages/AdminPage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { LandingPage } from '@/pages/LandingPage'
import { useHydrateSession } from '@/hooks/useHydrateSession'
import { setUnauthorizedHandler } from '@/api/client'
import { useAuthStore } from '@/store/useAuthStore'

function MainApp() {
  useHydrateSession()

  return (
    <div className="relative flex h-screen overflow-hidden">
      <div className="mesh-bg pointer-events-none absolute inset-0" />
      <div className="relative flex h-full w-full">
        <LeftSidebar />
        <ChatInterface />
      </div>
    </div>
  )
}

function AuthBootstrap({ children }) {
  const checkAuth = useAuthStore((s) => s.checkAuth)
  const handleUnauthorized = useAuthStore((s) => s.handleUnauthorized)
  const navigate = useNavigate()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  useEffect(() => {
    setUnauthorizedHandler(() => {
      handleUnauthorized()
      navigate('/login', { replace: true })
    })
    return () => setUnauthorizedHandler(null)
  }, [handleUnauthorized, navigate])

  return children
}

function ProtectedRoute({ children }) {
  const status = useAuthStore((s) => s.status)

  if (status === 'idle' || status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  if (status !== 'authenticated') {
    return <Navigate to="/login" replace />
  }

  return children
}

function AdminRoute({ children }) {
  const status = useAuthStore((s) => s.status)
  const isAdmin = useAuthStore((s) => Boolean(s.user?.is_admin))

  if (status === 'idle' || status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  if (status !== 'authenticated') {
    return <Navigate to="/login" replace />
  }

  if (!isAdmin) {
    return <Navigate to="/app" replace />
  }

  return children
}

function GuestRoute({ children }) {
  const status = useAuthStore((s) => s.status)

  if (status === 'idle' || status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  if (status === 'authenticated') {
    return <Navigate to="/app" replace />
  }

  return children
}

function AdminApp() {
  return (
    <div className="relative flex h-screen overflow-hidden">
      <div className="mesh-bg pointer-events-none absolute inset-0" />
      <div className="relative flex h-full w-full">
        <LeftSidebar />
        <AdminPage />
      </div>
    </div>
  )
}

export default function App() {
  return (
    <TooltipProvider delayDuration={200}>
      <BrowserRouter>
        <AuthBootstrap>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/login"
              element={
                <GuestRoute>
                  <LoginPage />
                </GuestRoute>
              }
            />
            <Route
              path="/register"
              element={
                <GuestRoute>
                  <RegisterPage />
                </GuestRoute>
              }
            />
            <Route
              path="/app"
              element={
                <ProtectedRoute>
                  <MainApp />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminApp />
                </AdminRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthBootstrap>
      </BrowserRouter>
    </TooltipProvider>
  )
}
