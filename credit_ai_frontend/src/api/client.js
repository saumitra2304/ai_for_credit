import { clearToken, getToken } from '@/lib/authStorage'
import { apiUrl, withInternalHeaders } from '@/lib/runtime'

export class UnauthorizedError extends Error {
  constructor(message = 'Unauthorized') {
    super(message)
    this.name = 'UnauthorizedError'
  }
}

let onUnauthorized = null

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

export async function authFetch(url, options = {}) {
  const token = getToken()
  const headers = withInternalHeaders(options.headers)

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(apiUrl(url), { ...options, headers })

  if (response.status === 401) {
    clearToken()
    onUnauthorized?.()
    throw new UnauthorizedError()
  }

  return response
}

export async function authJson(url, options = {}) {
  const response = await authFetch(url, options)

  if (!response.ok) {
    const text = await response.text()
    let message = text || response.statusText
    try {
      const json = JSON.parse(text)
      message = json.detail ?? json.message ?? message
      if (typeof message !== 'string') {
        message = JSON.stringify(message)
      }
    } catch {
      // Use raw text.
    }
    throw new Error(message)
  }

  return response.json()
}
