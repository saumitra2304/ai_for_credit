import { apiUrl, withInternalHeaders } from '@/lib/runtime'

export async function fetchOllamaStatus() {
  const response = await fetch(apiUrl('/api/ollama/status'), {
    headers: withInternalHeaders(),
  })
  if (!response.ok) {
    throw new Error(`Ollama status failed: ${response.statusText}`)
  }
  return response.json()
}

export async function startOllama() {
  const response = await fetch(apiUrl('/api/ollama/start'), {
    method: 'POST',
    headers: withInternalHeaders(),
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.error || 'Failed to start Ollama')
  }
  return payload
}

export async function warmupOllama() {
  const response = await fetch(apiUrl('/api/ollama/warmup'), {
    method: 'POST',
    headers: withInternalHeaders(),
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.error || 'Failed to warm up the model')
  }
  return payload
}

export async function pullOllamaModel(name, onProgress) {
  const response = await fetch(apiUrl('/api/ollama/pull'), {
    method: 'POST',
    headers: withInternalHeaders({
      'Content-Type': 'application/json',
    }),
    body: JSON.stringify(name ? { name } : {}),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Failed to pull model: ${response.statusText}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (!line.trim()) continue
      try {
        const event = JSON.parse(line)
        onProgress?.(event)
      } catch {
        // Ignore malformed NDJSON lines.
      }
    }
  }
}

export function progressFromPullEvent(event) {
  const total = Number(event?.total) || 0
  const completed = Number(event?.completed) || 0
  if (total > 0) {
    return Math.min(100, Math.round((completed / total) * 100))
  }
  if (event?.status === 'success') return 100
  return null
}
