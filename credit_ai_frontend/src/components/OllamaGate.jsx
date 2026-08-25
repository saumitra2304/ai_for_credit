import { useCallback, useEffect, useState } from 'react'
import { Download, Loader2, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { KuberLogo } from '@/components/KuberLogo'
import { getRuntimeConfig } from '@/lib/runtime'
import {
  fetchOllamaStatus,
  progressFromPullEvent,
  pullOllamaModel,
} from '@/api/ollama'

export function OllamaGate({ children }) {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
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

  const handlePull = async () => {
    setPulling(true)
    setError('')
    setPullProgress(0)
    setPullLabel('Starting download…')
    try {
      await pullOllamaModel(status?.model, (event) => {
        const pct = progressFromPullEvent(event)
        if (pct != null) setPullProgress(pct)
        if (event?.status) setPullLabel(event.status)
      })
      await refresh()
    } catch (err) {
      setError(err.message || 'Model download failed.')
    } finally {
      setPulling(false)
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

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      <div className="mesh-bg pointer-events-none absolute inset-0" />
      <div className="glass-panel relative w-full max-w-lg rounded-2xl border p-8 shadow-xl">
        <div className="mb-6 flex flex-col items-center text-center">
          <KuberLogo size={44} showWordmark />
          <p className="mt-2 text-sm text-muted-foreground">
            Local model setup
          </p>
        </div>

        {!status?.running ? (
          <div className="space-y-4 text-sm">
            <p className="text-foreground">
              Kuber uses Ollama on this machine for credit analysis. Install it,
              then come back here — models are not bundled with the app.
            </p>
            <a
              href="https://ollama.com/download"
              target="_blank"
              rel="noreferrer"
              className="inline-flex font-medium text-primary hover:underline"
            >
              Download Ollama
            </a>
          </div>
        ) : (
          <div className="space-y-4 text-sm">
            <p className="text-foreground">
              Ollama is running. Download <span className="font-medium">{model}</span> to
              continue. This is several gigabytes and only happens once.
            </p>
            {pulling && (
              <div className="space-y-2">
                <Progress value={pullProgress} />
                <p className="text-xs text-muted-foreground">{pullLabel}</p>
              </div>
            )}
          </div>
        )}

        {error && (
          <p className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
            {error}
          </p>
        )}

        <div className="mt-6 flex gap-2">
          <Button type="button" variant="outline" onClick={refresh} disabled={loading || pulling}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Check again
          </Button>
          {status?.running && !status?.installed && (
            <Button type="button" onClick={handlePull} disabled={pulling}>
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
