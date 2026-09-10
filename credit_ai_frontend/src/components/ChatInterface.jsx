import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, AlertCircle, Trash2, ArrowDown, Loader2, LogOut, BarChart3, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { ChatTurn } from '@/components/ChatMessage'
import { CompanyCharts } from '@/components/CompanyCharts'
import { ComposerExtras } from '@/components/ComposerExtras'
import { MemoComposer } from '@/components/MemoComposer'
import { ThemeToggle } from '@/components/ThemeToggle'
import { ThinkingPanel } from '@/components/ThinkingPanel'
import { KuberLogo } from '@/components/KuberLogo'
import { SidebarToggle } from '@/components/LeftSidebar'
import { useChatScroll } from '@/hooks/useChatScroll'
import {
  streamChatMessage,
  createProgressSimulator,
  getProgressForStage,
  stripStreamPrefix,
  hasDisplayableContent,
  downloadChatMemo,
} from '@/api/chat'
import { formatChatIdLabel } from '@/lib/chatId'
import { extraCinsText } from '@/lib/peerSelect'
import { groupMessagesIntoTurns, createTurnMessages } from '@/lib/messages'
import { saveChatSession, clearChatSession } from '@/lib/chatSessionStorage'
import { debounce } from '@/lib/utils'
import { isThinStream } from '@/lib/thinkingSteps'
import { useAppStore } from '@/store/useAppStore'
import { useAuthStore } from '@/store/useAuthStore'

const SUGGESTED_PROMPTS = [
  'Complete credit analysis',
  'Key strengths & red flags',
  'Debt structure summary',
  '3-year financial trends',
]

const MIN_THINK_MS = 8000
const FOLLOWUP_THINK_MS = 400

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
  const selectCompany = useAppStore((s) => s.selectCompany)

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState(null)
  const [error, setError] = useState(null)
  const [streamingMessageId, setStreamingMessageId] = useState(null)
  const [chartsOpen, setChartsOpen] = useState(false)
  const [memoOpen, setMemoOpen] = useState(false)
  const [memoLoading, setMemoLoading] = useState(false)
  const [extraPeers, setExtraPeers] = useState([])
  const [extraSearches, setExtraSearches] = useState('')
  const [chatFiles, setChatFiles] = useState([])
  const [revealAnswer, setRevealAnswer] = useState(false)
  const [pendingTurnId, setPendingTurnId] = useState(null)

  const scrollContainerRef = useRef(null)
  const contentRef = useRef(null)
  const { showScrollButton, enableAutoScroll, jumpToLatest } = useChatScroll(
    scrollContainerRef,
    contentRef
  )
  const simulatorRef = useRef(null)
  const abortRef = useRef(null)
  const autoKeyRef = useRef('')
  const runAnalysisRef = useRef(null)
  const revealRef = useRef(false)
  const thinkStartedRef = useRef(0)
  const streamBufferRef = useRef('')
  const revealTimerRef = useRef(null)
  const sessionRef = useRef({ activeChatId, selectedCompanies, messages, loading: false })

  const cinList = selectedCompanies.map((c) => c.cin)
  const turns = useMemo(() => groupMessagesIntoTurns(messages), [messages])
  const canDownloadMemo = Boolean(
    activeChatId &&
      !loading &&
      messages.some((msg) => msg.role === 'assistant' && String(msg.content || '').trim())
  )

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
    if (loading) return
    persistSessionDebounced({ interrupted: false })
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
    setRevealAnswer(false)
    setPendingTurnId(null)
    setMemoOpen(false)
    setExtraPeers([])
    setExtraSearches('')
    setChatFiles([])
    enableAutoScroll()
  }, [sessionKey, enableAutoScroll])

  useEffect(() => () => abortRef.current?.abort(), [])

  const runAnalysis = async (query, { hidePrompt = false, extras } = {}) => {
    const companies = sessionRef.current.selectedCompanies
    const cins = companies.map((c) => c.cin)
    if (!query || cins.length === 0) return

    const extraCins = extras?.extraCins ?? ''
    const extraSearchText = extras?.extraSearches ?? ''
    const files = extras?.files ?? []

    setError(null)
    setInput('')
    setLoading(true)
    setProgress((prev) => Math.max(prev, 8))
    const names = companies.map((c) => c.legalName).join(', ')
    const fetchStage = { id: 'fetch', label: `Loading company data for ${names}` }
    setCurrentStage(fetchStage)
    setRevealAnswer(false)
    revealRef.current = false
    streamBufferRef.current = ''
    const thinkFloor = hidePrompt ? MIN_THINK_MS : FOLLOWUP_THINK_MS
    thinkStartedRef.current = Date.now()
    enableAutoScroll()

    const { userMessage, assistantId, turnId } = createTurnMessages(query, {
      hidden: hidePrompt,
    })
    setPendingTurnId(turnId)
    updateMessages((prev) => [...prev, userMessage])

    simulatorRef.current = createProgressSimulator(setProgress, setCurrentStage, fetchStage)
    abortRef.current?.abort()
    abortRef.current = new AbortController()

    const paintAssistant = (displayText) => {
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
    }

    const maybeReveal = (displayText, force = false) => {
      streamBufferRef.current = displayText
      const waited = Date.now() - thinkStartedRef.current >= thinkFloor
      if (!force && (!waited || isThinStream(displayText))) return
      if (!revealRef.current) {
        revealRef.current = true
        setRevealAnswer(true)
      }
      paintAssistant(displayText)
    }

    const chatId = ensureChatId()
    if (revealTimerRef.current) clearTimeout(revealTimerRef.current)
    revealTimerRef.current = setTimeout(() => {
      if (streamBufferRef.current) maybeReveal(streamBufferRef.current)
    }, thinkFloor + 80)

    try {
      const response = await streamChatMessage({
        cinList: cins,
        query,
        chatId,
        extraCins,
        extraSearches: extraSearchText,
        files,
        signal: abortRef.current.signal,
        onStageChange: (stage) => {
          if (stage?.id && stage.id !== 'fetch') {
            simulatorRef.current?.cancel()
          }
          setCurrentStage(stage)
          setProgress((prev) => Math.max(prev, getProgressForStage(stage)))
        },
        onChunk: (_chunk, fullText) => {
          if (!hasDisplayableContent(fullText)) {
            setCurrentStage((prev) => prev ?? fetchStage)
            setProgress((prev) => Math.max(prev, 8))
            return
          }
          simulatorRef.current?.cancel()
          maybeReveal(stripStreamPrefix(fullText))
        },
      })

      const remaining = thinkFloor - (Date.now() - thinkStartedRef.current)
      if (remaining > 0) {
        await new Promise((resolve) => setTimeout(resolve, remaining))
      }
      const finalContent = stripStreamPrefix(response) || 'No response received.'
      maybeReveal(finalContent, true)

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
      if (revealTimerRef.current) {
        clearTimeout(revealTimerRef.current)
        revealTimerRef.current = null
      }
      simulatorRef.current?.complete()
      setLoading(false)
      setStreamingMessageId(null)
      setPendingTurnId(null)
      setProgress(100)
      abortRef.current = null
    }
  }

  runAnalysisRef.current = runAnalysis

  const handleSend = async (text) => {
    const typed = (text ?? input).trim()
    const extras = {
      extraCins: extraCinsText(extraPeers),
      extraSearches,
      files: chatFiles,
    }
    const hasExtras = Boolean(
      extras.extraCins.trim() || extras.extraSearches.trim() || extras.files.length
    )
    const query = typed || (hasExtras
      ? 'Use the extra peers, searches, and uploaded documents with this analysis.'
      : '')
    if (!query || loading) return
    if (cinList.length === 0) {
      setError('Select at least one company first.')
      return
    }
    setExtraPeers([])
    setExtraSearches('')
    setChatFiles([])
    await runAnalysis(query, { extras })
  }

  useEffect(() => {
    if (selectedCompanies.length === 0) {
      autoKeyRef.current = ''
      if (messages.length === 0) {
        setLoading(false)
        setCurrentStage(null)
        setProgress(0)
      }
      return
    }
    if (messages.length > 0) return
    const key = selectedCompanies.map((c) => c.cin).join(',')
    if (autoKeyRef.current === key) return
    autoKeyRef.current = key

    const names = selectedCompanies.map((c) => c.legalName).join(', ')
    let cancelled = false

    setError(null)
    setLoading(true)
    setRevealAnswer(false)
    setProgress(6)
    setCurrentStage({
      id: 'fetch',
      label: `Loading company data for ${names}`,
    })
    enableAutoScroll()

    const timer = setTimeout(() => {
      if (cancelled) return
      runAnalysisRef.current?.(`Complete credit analysis for ${names}`, { hidePrompt: true })
    }, 400)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [selectedCompanies, messages.length, sessionKey, enableAutoScroll])

  const clearChat = () => {
    updateMessages([])
    setError(null)
    setRevealAnswer(false)
    setPendingTurnId(null)
    clearChatSession()
    resetChat()
  }

  const handleLogout = async () => {
    clearChatSession()
    resetChat()
    await logout()
    navigate('/login', { replace: true })
  }

  const handleDownloadMemo = async (format, options = {}) => {
    if (!activeChatId || memoLoading) return
    setMemoLoading(true)
    setError(null)
    try {
      await downloadChatMemo(activeChatId, { format, ...options })
      setMemoOpen(false)
    } catch (err) {
      setError(err?.message || 'Could not download the credit memo.')
    } finally {
      setMemoLoading(false)
    }
  }

  return (
    <main key={sessionKey} className="flex h-full min-w-0 flex-1 flex-col">
      <header className="glass-panel relative z-40 shrink-0 overflow-hidden border-b pt-[env(safe-area-inset-top)]">
        <div className="flex h-12 items-center justify-between gap-2 px-2 sm:px-5">
        <div className="flex min-w-0 items-center gap-1.5 sm:gap-2">
          <SidebarToggle />
          <KuberLogo size={28} showWordmark className="min-w-0 [&_.kuber-wordmark]:hidden sm:[&_.kuber-wordmark]:inline" />
          <p className="hidden text-[10px] uppercase tracking-[0.16em] text-muted-foreground md:block">
            Credit workspace
          </p>
        </div>

        <div className="flex min-w-0 shrink-0 items-center gap-0.5 sm:gap-1">
          {activeChatId && (
            <Badge variant="outline" className="hidden h-5 px-1.5 font-mono text-[10px] sm:inline-flex">
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
          <ThemeToggle />
          {selectedCompanies.length > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 gap-1 px-2 text-xs"
                  onClick={() => setChartsOpen(true)}
                >
                  <BarChart3 className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">Show charts</span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>Financial and credit charts</TooltipContent>
            </Tooltip>
          )}
          {canDownloadMemo && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-7 gap-1 px-2 text-xs"
              disabled={memoLoading}
              onClick={() => setMemoOpen(true)}
            >
              {memoLoading ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Download className="h-3.5 w-3.5" />
              )}
              <span className="hidden sm:inline">
                {memoLoading ? 'Memo…' : 'Memo'}
              </span>
            </Button>
          )}
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
        </div>
      </header>

      <div className="relative min-h-0 flex-1">
        <CompanyCharts
          companies={selectedCompanies}
          open={chartsOpen}
          onClose={() => setChartsOpen(false)}
          onAddPeer={(company) => {
            if (!company?.cin) return
            selectCompany({
              id: company.cin,
              cin: company.cin,
              legalName: company.legalName || company.name,
              status: 'ACTIVE',
              type: 'company',
            })
            setExtraPeers((current) => {
              if (current.some((peer) => peer.cin === company.cin)) return current
              return [
                ...current,
                {
                  cin: company.cin,
                  legalName: company.legalName || company.name,
                  source: 'probe',
                },
              ]
            })
          }}
        />
        <MemoComposer
          open={memoOpen}
          loading={memoLoading}
          selectedCompanies={selectedCompanies}
          onClose={() => !memoLoading && setMemoOpen(false)}
          onGenerate={handleDownloadMemo}
        />
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
                  <div className="flex-1 text-amber-950 dark:text-amber-100/90">
                    <p className="font-medium text-amber-900 dark:text-amber-200">Session restored</p>
                    <p className="mt-0.5 text-amber-800/80 dark:text-amber-100/70">
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
                className="chat-content-width flex flex-col items-center px-1 py-10 text-center sm:py-16"
              >
                <KuberLogo size={40} className="sm:hidden" />
                <KuberLogo size={48} className="hidden sm:block" />
                <h2 className="font-display mt-5 text-[1.75rem] leading-tight sm:text-3xl">Name the borrower.</h2>
                <p className="mt-2 max-w-md text-sm leading-relaxed text-muted-foreground">
                  Search an Indian company in the sidebar. Kuber loads the filings and writes a
                  first credit pass — then you can chart it, add peers, and download the memo.
                </p>

                {selectedCompanies.length > 0 && (
                  <div className="mt-8 w-full max-w-2xl">
                    <p className="mb-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                      Suggestions
                    </p>
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                      {SUGGESTED_PROMPTS.map((prompt, i) => (
                        <motion.button
                          key={prompt}
                          initial={{ opacity: 0, y: 8 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.1 + i * 0.05 }}
                          type="button"
                          onClick={() => handleSend(prompt)}
                          className="rounded-xl border border-border/50 bg-card/50 px-3 py-3 text-left text-sm transition-colors hover:border-foreground/20 hover:bg-card"
                        >
                          {prompt}
                        </motion.button>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {turns.map((turn) => {
              const isPending = pendingTurnId && turn.user?.turnId === pendingTurnId
              if (isPending && !revealAnswer) {
                if (!turn.user || turn.user.hidden) return null
                return (
                  <ChatTurn
                    key={turn.user.turnId ?? turn.user.id}
                    turn={{ user: turn.user, assistant: null }}
                    streamingMessageId={null}
                  />
                )
              }
              return (
                <ChatTurn
                  key={turn.user?.turnId ?? turn.user?.id ?? turn.assistant?.id}
                  turn={turn}
                  streamingMessageId={streamingMessageId}
                />
              )
            })}

            <AnimatePresence>
              {loading && !revealAnswer && (
                <motion.div
                  key="thinking"
                  className="chat-content-width py-8"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.35 }}
                >
                  <ThinkingPanel
                    companyNames={selectedCompanies.map((company) => company.legalName)}
                    currentStage={currentStage}
                    progress={progress}
                  />
                </motion.div>
              )}
            </AnimatePresence>

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

      <div className="shrink-0 border-t border-border/40 px-3 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:px-4 sm:py-4">
        <div className="chat-content-width">
          <div className="flex items-end gap-3">
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
                className="min-h-[24px] flex-1 border-0 bg-transparent px-0 text-base shadow-none focus-visible:ring-0 sm:text-[15px]"
              />
            </div>
            <Button
              size="icon"
              className="h-10 w-10 shrink-0 rounded-xl"
              onClick={() => handleSend()}
              disabled={
                loading ||
                (!input.trim() &&
                  extraPeers.length === 0 &&
                  !extraSearches.trim() &&
                  chatFiles.length === 0)
              }
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <ComposerExtras
            disabled={loading || cinList.length === 0}
            extraPeers={extraPeers}
            extraSearches={extraSearches}
            files={chatFiles}
            excludeCins={cinList}
            onPeersChange={setExtraPeers}
            onSearchesChange={setExtraSearches}
            onFilesChange={setChatFiles}
          />
        </div>
      </div>
    </main>
  )
}
