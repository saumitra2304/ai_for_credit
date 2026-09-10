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
  extraCins = '',
  extraSearches = '',
  files = [],
  onChunk,
  onStageChange,
  signal,
}) {
  const hasExtras =
    String(extraCins || '').trim() ||
    String(extraSearches || '').trim() ||
    (files && files.length > 0)
  const response = await authFetch(CHAT_BASE, {
    method: 'POST',
    headers: {
      Accept: 'text/plain',
    },
    body: hasExtras
      ? buildChatForm({
          cinList,
          query,
          chatId,
          stream,
          extraCins,
          extraSearches,
          files,
        })
      : JSON.stringify({
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
    if (paintTimer) {
      clearTimeout(paintTimer)
      onStageChange?.(detectStreamStage(fullText), fullText)
      onChunk?.('', fullText)
    }
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
  { id: 'fetch', label: 'Loading company data', weight: 20 },
  { id: 'report', label: 'Writing credit assessment', weight: 80 },
]

export function detectStreamStage(text) {
  const content = stripStreamPrefix(text)

  if (content.trim().length > 0) {
    return ANALYSIS_STAGES.find((stage) => stage.id === 'report')
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

export function filenameFromDisposition(header, fallback) {
  const match = String(header || '').match(/filename\*?=(?:UTF-8''|"?)([^";]+)"?/i)
  if (!match) return fallback
  try {
    return decodeURIComponent(match[1])
  } catch {
    return match[1]
  }
}

export function buildMemoForm({
  format = 'pdf',
  notes = '',
  extraCins = '',
  extraSearches = '',
  includeChat = true,
  autoPeers = true,
  files = [],
} = {}) {
  const form = new FormData()
  form.append('format', format)
  form.append('notes', notes)
  form.append('extra_cins', extraCins)
  form.append('extra_searches', extraSearches)
  form.append('include_chat', includeChat ? 'true' : 'false')
  form.append('auto_peers', autoPeers ? 'true' : 'false')
  for (const file of files) {
    if (file) form.append('files', file)
  }
  return form
}

export function buildChatForm({
  cinList = [],
  query = '',
  chatId = '',
  stream = true,
  extraCins = '',
  extraSearches = '',
  files = [],
} = {}) {
  const form = new FormData()
  form.append('cin_list', JSON.stringify(cinList))
  form.append('query', query)
  form.append('chat_id', String(chatId ?? ''))
  form.append('stream', stream ? 'true' : 'false')
  form.append('extra_cins', extraCins)
  form.append('extra_searches', extraSearches)
  for (const file of files) {
    if (file) form.append('files', file)
  }
  return form
}

export async function downloadChatMemo(chatId, options = {}) {
  const format = typeof options === 'string' ? options : options.format || 'pdf'
  const payload = typeof options === 'string' ? { format } : { ...options, format }
  const response = await authFetch(
    `${CHAT_BASE}/${encodeURIComponent(chatId)}/memo?format=${encodeURIComponent(format)}`,
    { method: 'POST', body: buildMemoForm(payload) }
  )

  if (!response.ok) {
    const text = await response.text()
    let message = text || `Memo download failed: ${response.statusText}`
    try {
      const json = JSON.parse(text)
      const detail = json.detail ?? json.message
      if (typeof detail === 'string' && detail.trim()) message = detail
    } catch {
      // keep raw text
    }
    throw new Error(message)
  }

  const blob = await response.blob()
  const filename = filenameFromDisposition(
    response.headers.get('content-disposition'),
    `credit-memo.${format}`
  )
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
  return filename
}
