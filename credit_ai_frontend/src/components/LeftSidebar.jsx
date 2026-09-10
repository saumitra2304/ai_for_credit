import { Building2, History, Menu, Shield, X } from 'lucide-react'
import { useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CompanySearch } from '@/components/CompanySearch'
import { ChatHistory } from '@/components/ChatHistory'
import { KuberLogo } from '@/components/KuberLogo'
import { cn } from '@/lib/utils'
import { useAppStore } from '@/store/useAppStore'
import { useAuthStore } from '@/store/useAuthStore'

export function SidebarToggle() {
  const setMobileSidebarOpen = useAppStore((s) => s.setMobileSidebarOpen)
  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      className="h-8 w-8 shrink-0 lg:hidden"
      aria-label="Open sidebar"
      onClick={() => setMobileSidebarOpen(true)}
    >
      <Menu className="h-4 w-4" />
    </Button>
  )
}

export function LeftSidebar() {
  const sidebarTab = useAppStore((s) => s.sidebarTab)
  const setSidebarTab = useAppStore((s) => s.setSidebarTab)
  const startNewChat = useAppStore((s) => s.startNewChat)
  const loadSession = useAppStore((s) => s.loadSession)
  const mobileSidebarOpen = useAppStore((s) => s.mobileSidebarOpen)
  const setMobileSidebarOpen = useAppStore((s) => s.setMobileSidebarOpen)
  const isAdmin = useAuthStore((s) => Boolean(s.user?.is_admin))

  useEffect(() => {
    if (!mobileSidebarOpen) return undefined
    const onKey = (event) => {
      if (event.key === 'Escape') setMobileSidebarOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [mobileSidebarOpen, setMobileSidebarOpen])

  return (
    <>
      <button
        type="button"
        aria-label="Close sidebar"
        className={cn(
          'fixed inset-0 z-30 bg-black/45 transition-opacity lg:hidden',
          mobileSidebarOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        )}
        onClick={() => setMobileSidebarOpen(false)}
      />
      <aside
        className={cn(
          'glass-panel flex h-full w-[min(18rem,88vw)] flex-col border-r bg-background',
          'fixed inset-y-0 left-0 z-40 pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)] transition-transform duration-200 ease-out',
          'lg:static lg:z-auto lg:w-72 lg:shrink-0 lg:translate-x-0 lg:pt-0 lg:pb-0',
          mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="flex items-start justify-between border-b border-border/40 px-4 py-3">
          <div>
            <KuberLogo size={28} showWordmark />
            <p className="mt-1 text-[11px] uppercase tracking-[0.14em] text-muted-foreground">Credit workspace</p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-8 w-8 shrink-0 lg:hidden"
            aria-label="Close sidebar"
            onClick={() => setMobileSidebarOpen(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <Tabs
          value={sidebarTab}
          onValueChange={setSidebarTab}
          className="flex min-h-0 flex-1 flex-col px-3 pt-3"
        >
          <TabsList className="w-full shrink-0">
            <TabsTrigger value="search" className="flex-1">
              <Building2 className="h-3.5 w-3.5" />
              Search
            </TabsTrigger>
            <TabsTrigger value="history" className="flex-1">
              <History className="h-3.5 w-3.5" />
              History
            </TabsTrigger>
          </TabsList>

          <TabsContent value="search" className="mt-2 flex min-h-0 flex-1 flex-col">
            <CompanySearch />
          </TabsContent>

          <TabsContent value="history" className="mt-2 flex min-h-0 flex-1 flex-col">
            <ChatHistory
              onSelectSession={(session) => {
                loadSession(session)
                setSidebarTab('search')
              }}
              onNewChat={() => {
                startNewChat()
                setSidebarTab('search')
              }}
            />
          </TabsContent>
        </Tabs>

        {isAdmin && (
          <div className="border-t border-border/40 p-3">
            <NavLink
              to="/admin"
              onClick={() => setMobileSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                  isActive
                    ? 'bg-muted text-foreground'
                    : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
                }`
              }
            >
              <Shield className="h-3.5 w-3.5" />
              Admin
            </NavLink>
          </div>
        )}
      </aside>
    </>
  )
}
