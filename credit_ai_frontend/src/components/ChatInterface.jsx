import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, AlertCircle, Trash2, ArrowDown, Loader2, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { ChatTurn } from '@/components/ChatMessage'
import { AnalysisProgress } from '@/components/AnalysisProgress'
import { KuberLogo } from '@/components/KuberLogo'
import { useChatScroll } from '@/hooks/useChatScroll'
import {
  streamChatMessage,
  createProgressSimulator,
  getProgressForStage,
  stripStreamPrefix,
  hasDisplayableContent,
} from '@/api/chat'
import { formatChatIdLabel } from '@/lib/chatId'
import { groupMessagesIntoTurns, createTurnMessages } from '@/lib/messages'
import { saveChatSession, clearChatSession } from '@/lib/chatSessionStorage'
import { debounce } from '@/lib/utils'
import { useAppStore } from '@/store/useAppStore'
import { useAuthStore } from '@/store/useAuthStore'

const SUGGESTED_PROMPTS = [
  'Complete credit analysis',
  'Key strengths & red flags',
  'Debt structure summary',
  '3-year financial trends',
]

export function ChatInterface() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const sessionKey = useAppStore((s) => s.sessionKey)
  const activeChatId = useAppStore((s) => s.activeChatId)
  const selectedCompanies = useAppStore((s) => s.selectedCompanies)
  const messages = useAppStore((s) => s.messages)
  const recoveredNotice = useAppStore((s) => s.recoveredNotice)
  const updateMessages = useAppStore((s) => s.updateMessages)
  const ensureChatId = useAppStore((s) => s.ensureChatId)
  const resetChat = useAppStore((s) => s.resetChat)
  const completeChat = useAppStore((s) => s.completeChat)
  const dismissRecovered = useAppStore((s) => s.dismissRecovered)

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState(null)
  const [error, setError] = useState(null)
  const [streamingMessageId, setStreamingMessageId] = useState(null)

  const scrollContainerRef = useRef(null)
  const contentRef = useRef(null)
  const { showScrollButton, enableAutoScroll, jumpToLatest } = useChatScroll(
    scrollContainerRef,
    contentRef
  )
  const simulatorRef = useRef(null)
  const abortRef = useRef(null)
  const sessionRef = useRef({ activeChatId, selectedCompanies, messages, loading: false })

  const cinList = selectedCompanies.map((c) => c.cin)
  const turns = useMemo(() => groupMessagesIntoTurns(messages), [messages])

  const persistSession = useCallback((overrides = {}) => {
    const snapshot = sessionRef.current
    if (!snapshot.activeChatId && !overrides.activeChatId) return
    saveChatSession({
      activeChatId: overrides.activeChatId ?? snapshot.activeChatId,
      selectedCompanies: overrides.selectedCompanies ?? snapshot.selectedCompanies,
      messages: overrides.messages ?? snapshot.messages,
      interrupted: overrides.interrupted ?? false,
    })
  }, [])

  const persistSessionDebounced = useRef(
    debounce((overrides) => persistSession(overrides), 400)
  ).current

  useEffect(() => {
    sessionRef.current = { activeChatId, selectedCompanies, messages, loading }
  }, [activeChatId, selectedCompanies, messages, loading])

  useEffect(() => {
    if (messages.length === 0 && !loading) return
    persistSessionDebounced({ interrupted: loading })
  }, [messages, loading, activeChatId, selectedCompanies, persistSessionDebounced])

  useEffect(() => {
    const onPageHide = () => {
      if (sessionRef.current.loading) persistSession({ interrupted: true })
    }
    const onBeforeUnload = (event) => {
      if (!sessionRef.current.loading) return
      persistSession({ interrupted: true })
      event.preventDefault()
      event.returnValue = ''
    }
    window.addEventListener('pagehide', onPageHide)
    window.addEventListener('beforeunload', onBeforeUnload)
    return () => {
      window.removeEventListener('pagehide', onPageHide)
      window.removeEventListener('beforeunload', onBeforeUnload)
    }
  }, [persistSession])

  useEffect(() => {
    setError(null)
    enableAutoScroll()
  }, [sessionKey, enableAutoScroll])

  useEffect(() => () => abortRef.current?.abort(), [])

  const handleSend = async (text) => {
    const query = (text ?? input).trim()
    if (!query || loading) return

    if (cinList.length === 0) {
      setError('Select at least one company first.')
      return
    }

    setError(null)
    setInput('')
    setLoading(true)
    setProgress(0)
    setCurrentStage(null)
    enableAutoScroll()

    const { userMessage, assistantId, turnId } = createTurnMessages(query)
    updateMessages((prev) => [...prev, userMessage])

    simulatorRef.current = createProgressSimulator(setProgress, setCurrentStage)
    abortRef.current?.abort()
    abortRef.current = new AbortController()

    const chatId = ensureChatId()

    try {
      const response = await streamChatMessage({
        cinList,
        query,
        chatId,
        signal: abortRef.current.signal,
        onStageChange: (stage) => {
          simulatorRef.current?.cancel()
          setCurrentStage(stage)
          setProgress(getProgressForStage(stage))
        },
        onChunk: (_chunk, fullText) => {
          simulatorRef.current?.cancel()
          if (!hasDisplayableContent(fullText)) {
            setCurrentStage((prev) => prev ?? { id: 'fetch', label: 'Loading company data' })
            setProgress((prev) => Math.max(prev, 8))
            return
          }
          const displayText = stripStreamPrefix(fullText)
          setStreamingMessageId(assistantId)
          updateMessages((prev) => {
            const existing = prev.find((msg) => msg.id === assistantId)
            if (!existing) {
              return [
                ...prev,
                {
                  id: assistantId,
                  role: 'assistant',
                  content: displayText,
                  turnId,
                },
              ]
            }
            return prev.map((msg) =>
              msg.id === assistantId ? { ...msg, content: displayText } : msg
            )
          })
        },
      })

      const finalContent = stripStreamPrefix(response) || 'No response received.'
      updateMessages((prev) => {
        const existing = prev.find((msg) => msg.id === assistantId)
        if (!existing) {
          return [
            ...prev,
            { id: assistantId, role: 'assistant', content: finalContent, turnId },
          ]
        }
        return prev.map((msg) =>
          msg.id === assistantId ? { ...msg, content: finalContent } : msg
        )
      })

      completeChat()
      persistSession({ interrupted: false })
    } catch (err) {
      if (err.name === 'AbortError') {
        persistSession({ interrupted: true })
        return
      }
      simulatorRef.current?.cancel()
      updateMessages((prev) => {
        const assistant = prev.find((msg) => msg.id === assistantId)
        if (assistant?.content?.trim()) return prev
        return prev.filter((msg) => msg.id !== assistantId)
      })
      setError(err.message)
      persistSession({ interrupted: true })
    } finally {
      simulatorRef.current?.complete()
      setLoading(false)
      setStreamingMessageId(null)
      setProgress(100)
      abortRef.current = null
    }
  }

  const clearChat = () => {
    updateMessages([])
    setError(null)
    clearChatSession()
    resetChat()
  }

  const handleLogout = async () => {
    clearChatSession()
    resetChat()
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <main key={sessionKey} className="flex h-full flex-1 flex-col">
      <header className="glass-panel flex h-12 shrink-0 items-center justify-between border-b px-5">
        <div className="flex items-center gap-2.5">
          <KuberLogo size={28} showWordmark />
          <p className="text-[10px] text-muted-foreground">Intelligence workspace</p>
        </div>

        <div className="flex items-center gap-1.5">
          {activeChatId && (
            <Badge variant="outline" className="h-5 px-1.5 font-mono text-[10px]">
              {formatChatIdLabel(activeChatId)}
            </Badge>
          )}
          <Badge
            variant={selectedCompanies.length > 0 ? 'secondary' : 'outline'}
            className="hidden h-5 px-1.5 text-[10px] sm:flex"
          >
            {selectedCompanies.length > 0
              ? `${selectedCompanies.length} selected`
              : 'No company'}
          </Badge>
          {messages.length > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={clearChat}>
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Clear chat</TooltipContent>
            </Tooltip>
          )}
          {user && (
            <Badge variant="outline" className="hidden h-5 max-w-[140px] truncate px-1.5 text-[10px] lg:flex">
              {user.display_name || user.email}
            </Badge>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleLogout}>
                <LogOut className="h-3.5 w-3.5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Sign out</TooltipContent>
          </Tooltip>
        </div>
      </header>

      <div className="relative min-h-0 flex-1">
        <div
          ref={scrollContainerRef}
          className="chat-scroll-container h-full overflow-y-auto overflow-x-hidden scrollbar-thin overscroll-contain"
        >
          <div ref={contentRef} className="chat-scroll-content pb-6">
            <AnimatePresence>
              {recoveredNotice && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="chat-content-width mt-3 flex items-start gap-2 rounded-lg border border-amber-500/25 bg-amber-500/8 px-4 py-2.5 text-xs"
                >
                  <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-400" />
                  <div className="flex-1 text-amber-100/90">
                    <p className="font-medium text-amber-200">Session restored</p>
                    <p className="mt-0.5 text-amber-100/70">
                      Partial progress recovered after interruption.
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={dismissRecovered}>
                    OK
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>

            {messages.length === 0 && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="chat-content-width flex flex-col items-center py-16 text-center"
              >
                <KuberLogo size={48} />
                <h2 className="mt-4 text-lg font-semibold">Credit Intelligence</h2>
                <p className="mt-1 max-w-md text-sm text-muted-foreground">
                  Select a company and ask for financials, ratings, or risk analysis.
                </p>

                {selectedCompanies.length > 0 && (
                  <div className="mt-8 w-full max-w-2xl">
                    <p className="mb-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                      Suggestions
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      {SUGGESTED_PROMPTS.map((prompt, i) => (
                        <motion.button
                          key={prompt}
                          initial={{ opacity: 0, y: 8 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.1 + i * 0.05 }}
                          type="button"
                          onClick={() => handleSend(prompt)}
                          className="rounded-lg border border-border/40 bg-card/40 px-3 py-2.5 text-left text-sm transition-colors hover:border-primary/30 hover:bg-card/70"
                        >
                          {prompt}
                        </motion.button>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {turns.map((turn) => (
              <ChatTurn
                key={turn.user?.turnId ?? turn.user?.id ?? turn.assistant?.id}
                turn={turn}
                streamingMessageId={streamingMessageId}
              />
            ))}

            {loading && !streamingMessageId && (
              <div className="chat-content-width">
                <AnalysisProgress progress={progress} currentStage={currentStage} />
              </div>
            )}

            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="chat-content-width my-3 flex items-center gap-2 text-sm text-destructive"
              >
                <AlertCircle className="h-4 w-4 shrink-0" />
                {error}
              </motion.div>
            )}
          </div>
        </div>

        <AnimatePresence>
          {showScrollButton && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="absolute bottom-4 left-1/2 z-10 -translate-x-1/2"
            >
              <Button
                size="sm"
                variant="secondary"
                className="h-8 gap-1.5 rounded-full px-4 text-xs shadow-lg"
                onClick={jumpToLatest}
              >
                <ArrowDown className="h-3 w-3" />
                Jump to latest
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="shrink-0 border-t border-border/40 px-4 py-4">
        <div className="chat-content-width flex items-end gap-3">
          <div className="flex flex-1 items-center gap-2 rounded-2xl border border-border/50 bg-card/40 px-4 py-2.5 shadow-sm backdrop-blur-sm transition-shadow focus-within:border-primary/30 focus-within:ring-1 focus-within:ring-primary/15">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder={
                cinList.length > 0
                  ? 'Ask a follow-up about credit, financials, ratings...'
                  : 'Select a company first'
              }
              disabled={loading}
              className="min-h-[24px] flex-1 border-0 bg-transparent px-0 text-[15px] shadow-none focus-visible:ring-0"
            />
          </div>
          <Button
            size="icon"
            className="h-10 w-10 shrink-0 rounded-xl"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </main>
  )
}
