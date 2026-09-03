import { authFetch } from '@/api/client'

const CHAT_BASE = '/api/chat'

const LOADING_PREFIX = 'Loading company data...'

export function stripStreamPrefix(text) {
  return text.replace(/^Loading company data...\n?/, '')
}

export function hasDisplayableContent(text) {
  return stripStreamPrefix(text).trim().length > 0
}

export async function streamChatMessage({
  cinList,
  query,
  chatId = null,
  stream = true,
  onChunk,
  onStageChange,
  signal,
}) {
  const response = await authFetch(CHAT_BASE, {
    method: 'POST',
    headers: {
      Accept: 'text/plain',
    },
    body: JSON.stringify({
      cin_list: cinList,
      query,
      chat_id: chatId,
      stream,
    }),
    signal,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Chat request failed: ${response.statusText}`)
  }

  const contentType = response.headers.get('content-type') ?? ''

  if (!stream || !contentType.includes('text/plain')) {
    const text = await readPlainResponse(response)
    onStageChange?.(detectStreamStage(text), text)
    onChunk?.('', text)
    return stripStreamPrefix(text)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('Streaming is not supported in this browser.')
  }

  const decoder = new TextDecoder()
  let fullText = ''
  let lastPaint = 0
  let paintTimer = null
  const PAINT_MS = 48

  const emit = (chunk, force = false) => {
    const now = typeof performance !== 'undefined' ? performance.now() : Date.now()
    const flush = () => {
      paintTimer = null
      lastPaint = typeof performance !== 'undefined' ? performance.now() : Date.now()
      onStageChange?.(detectStreamStage(fullText), fullText)
      onChunk?.(chunk, fullText)
    }
    if (force || now - lastPaint >= PAINT_MS) {
      if (paintTimer) {
        clearTimeout(paintTimer)
        paintTimer = null
      }
      flush()
      return
    }
    if (!paintTimer) {
      paintTimer = setTimeout(flush, PAINT_MS - (now - lastPaint))
    }
  }

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      fullText += chunk
      emit(chunk)
    }

    const trailing = decoder.decode()
    if (trailing) {
      fullText += trailing
    }
    emit(trailing, true)
  } finally {
    if (paintTimer) clearTimeout(paintTimer)
  }

  return stripStreamPrefix(fullText)
}

async function readPlainResponse(response) {
  const contentType = response.headers.get('content-type') ?? ''

  if (contentType.includes('application/json')) {
    const json = await response.json()
    return typeof json === 'string' ? json : JSON.stringify(json, null, 2)
  }

  return response.text()
}

export const ANALYSIS_STAGES = [
  { id: 'fetch', label: 'Loading company data', weight: 12 },
  { id: 'credit', label: 'Generating per-company credit answer', weight: 22 },
  { id: 'news', label: 'Gathering per-company news', weight: 16 },
  { id: 'financials', label: 'Analyzing per-company financial detail', weight: 24 },
  { id: 'synthesis', label: 'Synthesizing final answer', weight: 16 },
  { id: 'report', label: 'Finalizing credit assessment report', weight: 10 },
]

export function detectStreamStage(text) {
  const content = stripStreamPrefix(text)

  if (content.includes('# Answer')) {
    return ANALYSIS_STAGES.find((stage) => stage.id === 'synthesis')
  }
  if (content.includes('# Per-Company Detail')) {
    return ANALYSIS_STAGES.find((stage) => stage.id === 'financials')
  }
  if (content.includes('# Per-Company News')) {
    return ANALYSIS_STAGES.find((stage) => stage.id === 'news')
  }
  if (content.includes('# Per-Company Credit Answer')) {
    return ANALYSIS_STAGES.find((stage) => stage.id === 'credit')
  }
  if (text.includes(LOADING_PREFIX)) {
    return ANALYSIS_STAGES.find((stage) => stage.id === 'fetch')
  }
  return ANALYSIS_STAGES[0]
}

export function getProgressForStage(stage) {
  if (!stage) return 0

  const stageIndex = ANALYSIS_STAGES.findIndex((item) => item.id === stage.id)
  if (stageIndex === -1) return 0

  const completedWeight = ANALYSIS_STAGES.slice(0, stageIndex).reduce(
    (sum, item) => sum + item.weight,
    0
  )

  return Math.min(completedWeight + Math.round(stage.weight * 0.6), 95)
}

export function createProgressSimulator(onProgress, onStageChange, initialStage) {
  let progress = 5
  let cancelled = false

  const tick = setInterval(() => {
    if (cancelled) return
    const remaining = 32 - progress
    progress = Math.min(progress + Math.max(0.18, remaining * 0.04), 32)
    onProgress(Math.round(progress))
    onStageChange(initialStage ?? ANALYSIS_STAGES[0])
  }, 180)

  return {
    complete() {
      cancelled = true
      clearInterval(tick)
      onProgress(100)
    },
    cancel() {
      cancelled = true
      clearInterval(tick)
    },
  }
}
