import { useCallback, useEffect, useState } from 'react'
import { Download, Loader2, Play, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { KuberLogo } from '@/components/KuberLogo'
import { getRuntimeConfig } from '@/lib/runtime'
import {
  fetchOllamaStatus,
  progressFromPullEvent,
  pullOllamaModel,
  startOllama,
  warmupOllama,
} from '@/api/ollama'

export function OllamaGate({ children }) {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [pulling, setPulling] = useState(false)
  const [pullProgress, setPullProgress] = useState(0)
  const [pullLabel, setPullLabel] = useState('')

  const refresh = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const next = await fetchOllamaStatus()
      setStatus(next)
    } catch (err) {
      if (!getRuntimeConfig().desktop) {
        setStatus({ running: true, installed: true, skip: true })
        return
      }
      setStatus({ ok: false, running: false, installed: false, model: 'qwen3:8b' })
      setError(err.message || 'Could not reach the local API.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const handlePull = async (modelName) => {
    setPulling(true)
    setError('')
    setPullProgress(0)
    setPullLabel('Starting download…')
    try {
      await pullOllamaModel(modelName, (event) => {
        const pct = progressFromPullEvent(event)
        if (pct != null) setPullProgress(pct)
        if (event?.status) setPullLabel(event.status)
      })
      await refresh()
      return true
    } catch (err) {
      setError(err.message || 'Model download failed.')
      return false
    } finally {
      setPulling(false)
    }
  }

  const handleStart = async () => {
    setBusy(true)
    setError('')
    try {
      const next = await startOllama()
      setStatus(next)
      const model = next?.model || status?.model || 'qwen3:8b'
      if (!next?.installed) {
        const pulled = await handlePull(model)
        if (!pulled) return
      }
      setPullLabel('Loading model into memory…')
      await warmupOllama()
      await refresh()
    } catch (err) {
      setError(err.message || 'Could not start the local model.')
      await refresh()
    } finally {
      setBusy(false)
    }
  }

  if (loading && !status) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  if (status?.running && status?.installed) {
    return children
  }

  const model = status?.model || 'qwen3:8b'
  const working = busy || pulling || loading

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      <div className="mesh-bg pointer-events-none absolute inset-0" />
      <div className="glass-panel relative w-full max-w-lg rounded-2xl border p-8 shadow-xl">
        <div className="mb-6 flex flex-col items-center text-center">
          <KuberLogo size={44} showWordmark />
          <p className="mt-2 text-sm text-muted-foreground">Local model setup</p>
        </div>

        <div className="space-y-4 text-sm">
          {!status?.running ? (
            <p className="text-foreground">
              Click <span className="font-medium">Start LLM</span> to launch Ollama with
              the credit-analysis settings (32k context, flash attention, q8 KV cache).
              You should not need a terminal.
            </p>
          ) : (
            <p className="text-foreground">
              Ollama is running. Download <span className="font-medium">{model}</span> to
              continue. This is several gigabytes and only happens once.
            </p>
          )}
          {!status?.binary_found && !status?.running && (
            <p className="text-muted-foreground">
              If Start LLM cannot find Ollama, install it once from{' '}
              <a
                href="https://ollama.com/download"
                target="_blank"
                rel="noreferrer"
                className="font-medium text-primary hover:underline"
              >
                ollama.com/download
              </a>
              , then click Start LLM again.
            </p>
          )}
          {(busy || pulling) && (
            <div className="space-y-2">
              <Progress value={pulling ? pullProgress : busy ? 12 : 0} />
              <p className="text-xs text-muted-foreground">
                {pullLabel || (busy ? 'Starting Ollama…' : '')}
              </p>
            </div>
          )}
        </div>

        {error && (
          <p className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
            {error}
          </p>
        )}

        <div className="mt-6 flex flex-wrap gap-2">
          <Button type="button" onClick={handleStart} disabled={working}>
            {busy && !pulling ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            Start LLM
          </Button>
          <Button type="button" variant="outline" onClick={refresh} disabled={working}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Check again
          </Button>
          {status?.running && !status?.installed && (
            <Button type="button" variant="secondary" onClick={() => handlePull(model)} disabled={working}>
              {pulling ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              {pulling ? 'Downloading…' : `Pull ${model}`}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
