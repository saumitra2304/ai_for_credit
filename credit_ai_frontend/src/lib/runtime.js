export function getRuntimeConfig() {
  if (typeof window === 'undefined') {
    return { apiOrigin: '', token: '', desktop: false }
  }

  return (
    window.__CREDIT_AI__ ?? {
      apiOrigin: '',
      token: '',
      desktop: false,
    }
  )
}

export function apiUrl(path) {
  const { apiOrigin } = getRuntimeConfig()
  if (!path) return apiOrigin || ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (!apiOrigin) return path
  return `${apiOrigin.replace(/\/$/, '')}${path}`
}

export function withInternalHeaders(initHeaders) {
  const headers = new Headers(initHeaders ?? {})
  const { token } = getRuntimeConfig()
  if (token) {
    headers.set('X-Internal-Token', token)
  }
  return headers
}
