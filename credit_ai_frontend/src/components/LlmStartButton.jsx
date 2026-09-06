import { useCallback, useEffect, useState } from 'react'
import { Loader2, Play, Power } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { fetchOllamaStatus, startOllama, stopOllama, warmupOllama } from '@/api/ollama'
import { cn } from '@/lib/utils'

export function LlmStartButton() {
  const [running, setRunning] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    try {
      const status = await fetchOllamaStatus()
      setRunning(Boolean(status?.running))
      setError('')
    } catch {
      setRunning(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    const tick = setInterval(refresh, 12000)
    return () => clearInterval(tick)
  }, [refresh])

  const handleStart = async () => {
    setBusy(true)
    setError('')
    try {
      await startOllama()
      await warmupOllama().catch(() => {})
      await refresh()
    } catch (err) {
      setError(err.message || 'Could not start the LLM')
    } finally {
      setBusy(false)
    }
  }

  const handleStop = async () => {
    setBusy(true)
    setError('')
    try {
      await stopOllama()
      await refresh()
    } catch (err) {
      setError(err.message || 'Could not stop the LLM')
      await refresh()
    } finally {
      setBusy(false)
    }
  }

  if (running) {
    return (
      <div className="flex items-center gap-1.5">
        <span className="hidden items-center gap-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400 sm:inline-flex">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          LLM ready
        </span>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className={cn('h-7 gap-1 px-2 text-xs', error && 'border-destructive/40')}
              onClick={handleStop}
              disabled={busy}
            >
              {busy ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Power className="h-3.5 w-3.5" />
              )}
              {busy ? 'Stopping…' : 'Stop LLM'}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {error || 'Stop Ollama and all of its processes'}
          </TooltipContent>
        </Tooltip>
      </div>
    )
  }

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className={cn('h-7 gap-1 px-2 text-xs', error && 'border-destructive/40')}
          onClick={handleStart}
          disabled={busy}
        >
          {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
          {busy ? 'Starting…' : 'Start LLM'}
        </Button>
      </TooltipTrigger>
      <TooltipContent>{error || 'Start Ollama with the Kuber serve settings'}</TooltipContent>
    </Tooltip>
  )
}
