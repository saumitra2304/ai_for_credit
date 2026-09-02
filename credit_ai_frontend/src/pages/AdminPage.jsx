import { useCallback, useEffect, useMemo, useState } from 'react'
import { ArrowLeft, KeyRound, Loader2, RefreshCw, Save, Activity, ListTree, ScrollText } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import * as adminApi from '@/api/admin'

const SETTING_LABELS = {
  probe_api_key: 'Probe API key',
  INSTA_API_KEY: 'InstaFinancials API key',
  OPENAI_API_KEY: 'OpenAI / Ollama API key',
  OPENAI_BASE_URL: 'OpenAI base URL',
  OPENAI_MODEL_NAME: 'Model name',
  SEARCH_API_KEY: 'Search API key',
}

function formatTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function durationMs(start, end) {
  const a = new Date(start).getTime()
  const b = new Date(end || start).getTime()
  if (Number.isNaN(a) || Number.isNaN(b)) return 0
  return Math.max(0, b - a)
}

export function AdminPage() {
  const [tab, setTab] = useState('keys')

  return (
    <main className="flex h-full min-w-0 flex-1 flex-col">
      <header className="glass-panel flex h-12 shrink-0 items-center justify-between border-b px-5">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/">
              <ArrowLeft className="h-3.5 w-3.5" />
              Chat
            </Link>
          </Button>
          <h1 className="text-sm font-semibold">Admin</h1>
        </div>
        <p className="text-xs text-muted-foreground">Keys, logs, traces, and metrics</p>
      </header>

      <Tabs value={tab} onValueChange={setTab} className="flex min-h-0 flex-1 flex-col px-5 py-4">
        <TabsList className="w-fit shrink-0">
          <TabsTrigger value="keys">
            <KeyRound className="h-3.5 w-3.5" />
            Keys
          </TabsTrigger>
          <TabsTrigger value="logs">
            <ScrollText className="h-3.5 w-3.5" />
            Logs
          </TabsTrigger>
          <TabsTrigger value="traces">
            <ListTree className="h-3.5 w-3.5" />
            Traces
          </TabsTrigger>
          <TabsTrigger value="metrics">
            <Activity className="h-3.5 w-3.5" />
            Metrics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="keys" className="mt-4 min-h-0 flex-1 overflow-hidden">
          <KeysTab />
        </TabsContent>
        <TabsContent value="logs" className="mt-4 min-h-0 flex-1 overflow-hidden">
          <LogsTab active={tab === 'logs'} />
        </TabsContent>
        <TabsContent value="traces" className="mt-4 min-h-0 flex-1 overflow-hidden">
          <TracesTab active={tab === 'traces'} />
        </TabsContent>
        <TabsContent value="metrics" className="mt-4 min-h-0 flex-1 overflow-hidden">
          <MetricsTab active={tab === 'metrics'} />
        </TabsContent>
      </Tabs>
    </main>
  )
}

function KeysTab() {
  const [settings, setSettings] = useState([])
  const [drafts, setDrafts] = useState({})
  const [dirty, setDirty] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await adminApi.fetchSettings()
      setSettings(data.settings ?? [])
      setDrafts({})
      setDirty({})
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const onChange = (key, value) => {
    setDrafts((prev) => ({ ...prev, [key]: value }))
    setDirty((prev) => ({ ...prev, [key]: true }))
    setSaved(false)
  }

  const onSave = async (event) => {
    event.preventDefault()
    const values = {}
    for (const setting of settings) {
      if (!dirty[setting.key]) continue
      values[setting.key] = drafts[setting.key] ?? ''
    }
    if (!Object.keys(values).length) return
    setSaving(true)
    setError(null)
    try {
      const data = await adminApi.saveSettings(values)
      setSettings(data.settings ?? [])
      setDrafts({})
      setDirty({})
      setSaved(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <Loader2 className="h-5 w-5 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle className="text-base">Runtime keys</CardTitle>
        <CardDescription>
          Saved values override bundled env in SQLite. Leave a secret blank to keep the current
          value; clear a non-secret to fall back to env defaults.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSave} className="space-y-4">
          {settings.map((setting) => {
            const secret = setting.secret
            const value = dirty[setting.key]
              ? (drafts[setting.key] ?? '')
              : secret
                ? ''
                : (setting.value ?? '')
            return (
              <div key={setting.key} className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">
                  {SETTING_LABELS[setting.key] || setting.key}
                </label>
                <Input
                  type={secret ? 'password' : 'text'}
                  autoComplete="off"
                  placeholder={secret ? setting.masked || 'bundled default' : ''}
                  value={value}
                  onChange={(event) => onChange(setting.key, event.target.value)}
                />
              </div>
            )
          })}

          {error && (
            <p className="rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          )}
          {saved && <p className="text-sm text-emerald-600">Settings saved.</p>}

          <Button type="submit" disabled={saving || !Object.keys(dirty).length}>
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Save
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

function levelVariant(level) {
  if (level === 'error') return 'destructive'
  if (level === 'warn' || level === 'warning') return 'warning'
  if (level === 'info') return 'default'
  return 'secondary'
}

function sourceClass(source) {
  const map = {
    agent: 'bg-sky-500/15 text-sky-700 dark:text-sky-300',
    llm: 'bg-violet-500/15 text-violet-700 dark:text-violet-300',
    search: 'bg-amber-500/15 text-amber-800 dark:text-amber-300',
    probe: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300',
    http: 'bg-muted text-muted-foreground',
    rust: 'bg-orange-500/15 text-orange-800 dark:text-orange-300',
    python: 'bg-primary/10 text-primary',
  }
  return map[source] || 'bg-muted text-muted-foreground'
}

function LogsTab({ active }) {
  const [logs, setLogs] = useState([])
  const [level, setLevel] = useState('')
  const [source, setSource] = useState('')
  const [query, setQuery] = useState('')
  const [error, setError] = useState(null)
  const [openId, setOpenId] = useState(null)

  const load = useCallback(async () => {
    try {
      const data = await adminApi.fetchLogs({
        level: level || undefined,
        source: source || undefined,
        q: query || undefined,
      })
      setLogs(data.logs ?? [])
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }, [level, source, query])

  useEffect(() => {
    if (!active) return undefined
    load()
    const id = setInterval(load, 3000)
    return () => clearInterval(id)
  }, [active, load])

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <select
          className="h-9 rounded-md border border-input bg-transparent px-2 text-sm"
          value={level}
          onChange={(event) => setLevel(event.target.value)}
        >
          <option value="">All levels</option>
          <option value="info">info</option>
          <option value="warn">warn</option>
          <option value="error">error</option>
        </select>
        <select
          className="h-9 rounded-md border border-input bg-transparent px-2 text-sm"
          value={source}
          onChange={(event) => setSource(event.target.value)}
        >
          <option value="">All sources</option>
          <option value="agent">agent</option>
          <option value="llm">llm</option>
          <option value="search">search</option>
          <option value="probe">probe</option>
          <option value="http">http</option>
          <option value="rust">rust</option>
          <option value="python">python</option>
        </select>
        <Input
          className="max-w-xs"
          placeholder="Search message or request id"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <Button variant="outline" size="sm" onClick={load}>
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </Button>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <ScrollArea className="min-h-0 flex-1 rounded-xl border bg-card">
        <div className="divide-y font-mono text-xs">
          {logs.length === 0 && (
            <p className="p-4 text-sm text-muted-foreground">No logs yet. Run an analysis to see agent steps.</p>
          )}
          {logs.map((log) => (
            <button
              key={log.id}
              type="button"
              onClick={() => setOpenId(openId === log.id ? null : log.id)}
              className="flex w-full flex-col gap-1 px-4 py-2 text-left hover:bg-muted/40"
            >
              <div className="flex items-start gap-3">
                <span className="w-40 shrink-0 text-muted-foreground">{formatTime(log.ts)}</span>
                <Badge variant={levelVariant(log.level)} className="h-5 shrink-0">
                  {log.level}
                </Badge>
                <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${sourceClass(log.source)}`}>
                  {log.source}
                </span>
                <span className="min-w-0 flex-1 break-all text-[12px] leading-relaxed">{log.message}</span>
                {log.request_id && (
                  <span className="w-28 shrink-0 truncate text-muted-foreground">{log.request_id}</span>
                )}
              </div>
              {openId === log.id && log.extra && (
                <pre className="ml-40 overflow-x-auto rounded-md bg-muted/50 p-2 text-[11px] text-muted-foreground">
                  {JSON.stringify(log.extra, null, 2)}
                </pre>
              )}
            </button>
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}

function TracesTab({ active }) {
  const [traces, setTraces] = useState([])
  const [selected, setSelected] = useState(null)
  const [spans, setSpans] = useState([])
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    try {
      const data = await adminApi.fetchTraces()
      setTraces(data.traces ?? [])
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  useEffect(() => {
    if (!active) return undefined
    load()
    const id = setInterval(load, 5000)
    return () => clearInterval(id)
  }, [active, load])

  const openTrace = async (traceId) => {
    setSelected(traceId)
    try {
      const data = await adminApi.fetchTrace(traceId)
      setSpans(data.spans ?? [])
    } catch (err) {
      setError(err.message)
    }
  }

  const maxDuration = useMemo(() => {
    if (!spans.length) return 1
    const rootStart = Math.min(...spans.map((span) => new Date(span.start_ts).getTime()))
    const rootEnd = Math.max(
      ...spans.map((span) => new Date(span.end_ts || span.start_ts).getTime()),
    )
    return Math.max(1, rootEnd - rootStart)
  }, [spans])

  const origin = useMemo(() => {
    if (!spans.length) return 0
    return Math.min(...spans.map((span) => new Date(span.start_ts).getTime()))
  }, [spans])

  const spanColor = (name, status) => {
    if (status !== 'ok') return 'bg-destructive/80'
    if (name.startsWith('llm')) return 'bg-violet-500/80'
    if (name.includes('search') || name === 'news') return 'bg-amber-500/80'
    if (name.includes('probe') || name === 'load_company_data') return 'bg-emerald-500/80'
    if (name === 'credit') return 'bg-sky-500/80'
    if (name === 'chat' || name === 'followup.answer' || name === 'synthesis') return 'bg-primary/80'
    return 'bg-primary/70'
  }

  return (
    <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[300px_1fr]">
      <ScrollArea className="min-h-0 rounded-xl border bg-card">
        <div className="divide-y">
          {traces.length === 0 && (
            <p className="p-4 text-sm text-muted-foreground">No traces yet. Run a chat to record agent steps.</p>
          )}
          {traces.map((trace) => (
            <button
              key={trace.trace_id}
              type="button"
              onClick={() => openTrace(trace.trace_id)}
              className={`block w-full px-3 py-2.5 text-left text-sm hover:bg-muted/60 ${
                selected === trace.trace_id ? 'bg-muted' : ''
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium">{trace.name || 'request'}</span>
                {trace.errors > 0 ? (
                  <Badge variant="destructive">{trace.errors}</Badge>
                ) : (
                  <Badge variant="success">{trace.spans}</Badge>
                )}
              </div>
              <p className="truncate font-mono text-[11px] text-muted-foreground">{trace.trace_id}</p>
              <p className="text-[11px] text-muted-foreground">
                {formatTime(trace.start_ts)} · {trace.spans} spans
              </p>
            </button>
          ))}
        </div>
      </ScrollArea>

      <ScrollArea className="min-h-0 rounded-xl border bg-card p-4">
        {error && <p className="mb-3 text-sm text-destructive">{error}</p>}
        {!selected && <p className="text-sm text-muted-foreground">Select a trace to see agent steps.</p>}
        {selected && (
          <div className="space-y-3">
            {spans.map((span) => {
              const left = ((new Date(span.start_ts).getTime() - origin) / maxDuration) * 100
              const width = Math.max(2, (durationMs(span.start_ts, span.end_ts) / maxDuration) * 100)
              return (
                <div key={span.span_id} className="space-y-1 rounded-lg border border-border/40 bg-muted/15 px-3 py-2">
                  <div className="flex items-center justify-between gap-2 text-xs">
                    <span className="font-medium">{span.name}</span>
                    <span className="tabular-nums text-muted-foreground">
                      {durationMs(span.start_ts, span.end_ts)}ms · {span.status}
                    </span>
                  </div>
                  <div className="relative h-3.5 overflow-hidden rounded-full bg-muted">
                    <div
                      className={`absolute top-0 h-full rounded-full ${spanColor(span.name, span.status)}`}
                      style={{ left: `${left}%`, width: `${width}%` }}
                    />
                  </div>
                  {span.attrs && (
                    <p className="truncate font-mono text-[10px] text-muted-foreground">
                      {Object.entries(span.attrs)
                        .map(([key, value]) => `${key}=${value}`)
                        .join(' · ')}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}

function MetricsTab({ active }) {
  const [metrics, setMetrics] = useState(null)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    try {
      const data = await adminApi.fetchMetrics(15)
      setMetrics(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  useEffect(() => {
    if (!active) return undefined
    load()
    const id = setInterval(load, 5000)
    return () => clearInterval(id)
  }, [active, load])

  const maxCount = Math.max(1, ...(metrics?.buckets ?? []).map((bucket) => bucket.count))

  return (
    <div className="flex h-full min-h-0 flex-col gap-4">
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="grid gap-3 sm:grid-cols-4">
        <Stat label="Requests" value={metrics?.count ?? 0} />
        <Stat label="Errors" value={metrics?.errors ?? 0} />
        <Stat label="Error rate" value={`${((metrics?.error_rate ?? 0) * 100).toFixed(1)}%`} />
        <Stat label="p95" value={`${metrics?.p95_ms ?? 0} ms`} />
      </div>
      <Card className="min-h-0 flex-1">
        <CardHeader>
          <CardTitle className="text-base">Request rate (15 min)</CardTitle>
          <CardDescription>One bar per minute. Red ticks are errors.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-48 items-end gap-px">
            {(metrics?.buckets ?? []).map((bucket) => (
              <div key={bucket.ts} className="flex min-w-0 flex-1 flex-col justify-end gap-px">
                <div
                  className="w-full rounded-t bg-destructive/80"
                  style={{ height: `${(bucket.errors / maxCount) * 100}%` }}
                  title={`${formatTime(bucket.ts)} errors ${bucket.errors}`}
                />
                <div
                  className="w-full rounded-t bg-primary/70"
                  style={{ height: `${(bucket.count / maxCount) * 100}%` }}
                  title={`${formatTime(bucket.ts)} ${bucket.count} req`}
                />
              </div>
            ))}
            {(!metrics?.buckets || metrics.buckets.length === 0) && (
              <p className="text-sm text-muted-foreground">No samples yet.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <Card>
      <CardHeader className="p-4">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-2xl">{value}</CardTitle>
      </CardHeader>
    </Card>
  )
}
