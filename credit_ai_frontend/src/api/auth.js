import { authFetch } from '@/api/client'
import { setToken } from '@/lib/authStorage'
import { apiUrl, withInternalHeaders } from '@/lib/runtime'

const AUTH_BASE = '/api/auth'

function applyAuthResponse(data) {
  if (data?.token) {
    setToken(data.token)
  }
  return data
}

async function parseErrorResponse(response) {
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

export async function register({ email, password, displayName }) {
  const response = await fetch(apiUrl(`${AUTH_BASE}/register`), {
    method: 'POST',
    headers: withInternalHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      email,
      password,
      display_name: displayName,
    }),
  })

  if (!response.ok) {
    await parseErrorResponse(response)
  }

  return applyAuthResponse(await response.json())
}

export async function login({ email, password }) {
  const response = await fetch(apiUrl(`${AUTH_BASE}/login`), {
    method: 'POST',
    headers: withInternalHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    await parseErrorResponse(response)
  }

  return applyAuthResponse(await response.json())
}

export async function logout() {
  try {
    await authFetch(`${AUTH_BASE}/logout`, { method: 'POST' })
  } catch {
    // Token may already be invalid.
  }
}

export async function fetchCurrentUser() {
  const response = await authFetch(`${AUTH_BASE}/me`)
  if (!response.ok) {
    await parseErrorResponse(response)
  }
  const data = await response.json()
  return data.user
}
