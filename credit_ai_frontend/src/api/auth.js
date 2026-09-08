import { authFetch } from '@/api/client'
import { setToken } from '@/lib/authStorage'
import { apiUrl, withInternalHeaders } from '@/lib/runtime'
import { friendlyAuthMessage } from '@/lib/authErrors'

const AUTH_BASE = '/api/auth'

function applyAuthResponse(data) {
  if (data?.token) {
    setToken(data.token)
  }
  return data
}

async function parseErrorResponse(response) {
  const text = await response.text()
  let raw = text || response.statusText
  try {
    const json = JSON.parse(text)
    raw = json.detail ?? json.message ?? raw
  } catch {
    // Use raw text.
  }
  throw new Error(friendlyAuthMessage(raw, response.status))
}

export async function register({ email, password, displayName }) {
  let response
  try {
    response = await fetch(apiUrl(`${AUTH_BASE}/register`), {
      method: 'POST',
      headers: withInternalHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        email,
        password,
        display_name: displayName,
      }),
    })
  } catch (err) {
    throw new Error(friendlyAuthMessage(err))
  }

  if (!response.ok) {
    await parseErrorResponse(response)
  }

  return applyAuthResponse(await response.json())
}

export async function login({ email, password }) {
  let response
  try {
    response = await fetch(apiUrl(`${AUTH_BASE}/login`), {
      method: 'POST',
      headers: withInternalHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ email, password }),
    })
  } catch (err) {
    throw new Error(friendlyAuthMessage(err))
  }

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
