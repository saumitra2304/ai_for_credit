import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { MessageSquare, Plus, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { fetchChatHistory, fetchChatSession, parseChatSession } from '@/api/chatHistory'
import { formatChatIdLabel } from '@/lib/chatId'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'

function sortSessions(sessions) {
  return [...sessions].sort((a, b) => {
    if (a.messageCount !== b.messageCount) return b.messageCount - a.messageCount
    return String(b.chatId).localeCompare(String(a.chatId))
  })
}

export function ChatHistory({ onSelectSession, onNewChat }) {
  const activeChatId = useAppStore((s) => s.activeChatId)
  const historyVersion = useAppStore((s) => s.historyVersion)

  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadHistory = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await fetchChatHistory()
      const parsed = sortSessions(
        (Array.isArray(data) ? data : [])
          .map(parseChatSession)
          .filter((session) => session.messageCount > 0)
      )
      setSessions(parsed)
    } catch (err) {
      setError(err.message)
      setSessions([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadHistory()
  }, [loadHistory, historyVersion])

  return (
    <div className="flex h-full min-h-0 flex-col pt-2">
      <div className="mb-2 flex items-center justify-end gap-0.5 px-1">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={loadHistory}
              disabled={loading}
            >
              <RefreshCw className={cn('h-3.5 w-3.5', loading && 'animate-spin')} />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Refresh</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onNewChat}>
              <Plus className="h-3.5 w-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>New chat</TooltipContent>
        </Tooltip>
      </div>

      <ScrollArea className="flex-1 scrollbar-thin">
        <div className="space-y-1 px-1 pb-2">
          {loading &&
            [...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-14 w-full rounded-lg" />
            ))}

          {!loading && error && (
            <p className="rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive">
              {error}
            </p>
          )}

          {!loading && !error && sessions.length === 0 && (
            <p className="py-8 text-center text-xs text-muted-foreground">
              No conversations yet
            </p>
          )}

          {sessions.map((session, i) => {
            const isActive = activeChatId === session.chatId
            const companyName = session.companies[0]?.legalName ?? 'Unknown'

            return (
              <motion.button
                key={session.chatId}
                type="button"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(i, 8) * 0.04 }}
                onClick={async () => {
                  try {
                    const full = await fetchChatSession(session.chatId)
                    onSelectSession(full ?? session)
                  } catch (err) {
                    setError(err.message)
                  }
                }}
                className={cn(
                  'w-full rounded-lg border px-2.5 py-2 text-left transition-all duration-200',
                  isActive
                    ? 'border-primary/40 bg-primary/10'
                    : 'border-border/40 bg-background/30 hover:border-primary/25 hover:bg-background/50'
                )}
              >
                <div className="flex items-start gap-2">
                  <MessageSquare
                    className={cn(
                      'mt-0.5 h-3 w-3 shrink-0',
                      isActive ? 'text-primary' : 'text-muted-foreground'
                    )}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-medium">{companyName}</p>
                    <p className="mt-0.5 line-clamp-1 text-[10px] text-muted-foreground">
                      {session.preview}
                    </p>
                    <p className="mt-1 text-[9px] text-muted-foreground/70">
                      {formatChatIdLabel(session.chatId)} · {session.messageCount} msg
                    </p>
                  </div>
                </div>
              </motion.button>
            )
          })}
        </div>
      </ScrollArea>
    </div>
  )
}
