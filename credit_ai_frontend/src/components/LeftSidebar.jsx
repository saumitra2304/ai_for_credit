import { Building2, History } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CompanySearch } from '@/components/CompanySearch'
import { ChatHistory } from '@/components/ChatHistory'
import { KuberLogo } from '@/components/KuberLogo'
import { useAppStore } from '@/store/useAppStore'

export function LeftSidebar() {
  const sidebarTab = useAppStore((s) => s.sidebarTab)
  const setSidebarTab = useAppStore((s) => s.setSidebarTab)
  const startNewChat = useAppStore((s) => s.startNewChat)
  const loadSession = useAppStore((s) => s.loadSession)

  return (
    <aside className="glass-panel flex h-full w-[288px] shrink-0 flex-col border-r">
      <div className="border-b border-border/40 px-4 py-3">
        <KuberLogo size={28} showWordmark />
        <p className="mt-1 text-xs text-muted-foreground">Credit intelligence</p>
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
    </aside>
  )
}
