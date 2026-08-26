import { authJson } from '@/api/client'

const ADMIN_BASE = '/api/admin'

export function fetchSettings() {
  return authJson(`${ADMIN_BASE}/settings`)
}

export function saveSettings(values) {
  return authJson(`${ADMIN_BASE}/settings`, {
    method: 'PUT',
    body: JSON.stringify({ values }),
  })
}

export function fetchLogs({ level, source, q, limit } = {}) {
  const params = new URLSearchParams()
  if (level) params.set('level', level)
  if (source) params.set('source', source)
  if (q) params.set('q', q)
  if (limit) params.set('limit', String(limit))
  const query = params.toString()
  return authJson(`${ADMIN_BASE}/logs${query ? `?${query}` : ''}`)
}

export function fetchTraces(limit = 50) {
  return authJson(`${ADMIN_BASE}/traces?limit=${limit}`)
}

export function fetchTrace(traceId) {
  return authJson(`${ADMIN_BASE}/traces/${encodeURIComponent(traceId)}`)
}

export function fetchMetrics(minutes = 15) {
  return authJson(`${ADMIN_BASE}/metrics?minutes=${minutes}`)
}
