import { useEffect } from 'react'
import { BrowserRouter, HashRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { TooltipProvider } from '@/components/ui/tooltip'
import { LeftSidebar } from '@/components/LeftSidebar'
import { ChatInterface } from '@/components/ChatInterface'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { useHydrateSession } from '@/hooks/useHydrateSession'
import { setUnauthorizedHandler } from '@/api/client'
import { useAuthStore } from '@/store/useAuthStore'
import { OllamaGate } from '@/components/OllamaGate'
import { getRuntimeConfig } from '@/lib/runtime'

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
  const status = useAuthStore((s) => s.status)
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

  if (status === 'idle' || status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  return children
}

function ProtectedRoute({ children }) {
  const status = useAuthStore((s) => s.status)

  if (status !== 'authenticated') {
    return <Navigate to="/login" replace />
  }

  return children
}

function GuestRoute({ children }) {
  const status = useAuthStore((s) => s.status)

  if (status === 'authenticated') {
    return <Navigate to="/" replace />
  }

  return children
}

export default function App() {
  const Router = getRuntimeConfig().desktop ? HashRouter : BrowserRouter

  return (
    <TooltipProvider delayDuration={200}>
      <Router>
        <OllamaGate>
          <AuthBootstrap>
            <Routes>
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
                path="/"
                element={
                  <ProtectedRoute>
                    <MainApp />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AuthBootstrap>
        </OllamaGate>
      </Router>
    </TooltipProvider>
  )
}
