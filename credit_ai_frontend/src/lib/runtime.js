export function getRuntimeConfig() {
  if (typeof window === 'undefined') {
    return { apiOrigin: '', token: '' }
  }

  const viteOrigin = String(import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
  return {
    apiOrigin: viteOrigin,
    token: '',
  }
}

export function apiUrl(path) {
  const { apiOrigin } = getRuntimeConfig()
  if (!path) return apiOrigin || ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (!apiOrigin) return path
  return `${apiOrigin.replace(/\/$/, '')}${path}`
}

export function withInternalHeaders(initHeaders) {
  return new Headers(initHeaders ?? {})
}
