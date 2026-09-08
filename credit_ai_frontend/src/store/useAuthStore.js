import { create } from 'zustand'
import * as authApi from '@/api/auth'
import { clearToken, getToken } from '@/lib/authStorage'
import { friendlyAuthMessage } from '@/lib/authErrors'

function initialStatus() {
  try {
    return getToken() ? 'idle' : 'unauthenticated'
  } catch {
    return 'unauthenticated'
  }
}

export const useAuthStore = create((set) => ({
  user: null,
  status: initialStatus(),
  error: null,

  clearError: () => set({ error: null }),

  login: async (email, password) => {
    set({ error: null })
    try {
      const data = await authApi.login({ email, password })
      set({ user: data.user, status: 'authenticated', error: null })
      return data
    } catch (err) {
      set({
        status: 'unauthenticated',
        error: friendlyAuthMessage(err, err.status),
      })
      throw err
    }
  },

  register: async (email, password, displayName) => {
    set({ error: null })
    try {
      const data = await authApi.register({ email, password, displayName })
      set({ user: data.user, status: 'authenticated', error: null })
      return data
    } catch (err) {
      set({
        status: 'unauthenticated',
        error: friendlyAuthMessage(err, err.status),
      })
      throw err
    }
  },

  logout: async () => {
    await authApi.logout()
    clearToken()
    set({ user: null, status: 'unauthenticated', error: null })
  },

  handleUnauthorized: () => {
    clearToken()
    set({ user: null, status: 'unauthenticated', error: null })
  },

  checkAuth: async () => {
    const token = getToken()
    if (!token) {
      set({ user: null, status: 'unauthenticated' })
      return false
    }

    set({ status: 'loading', error: null })
    try {
      const user = await authApi.fetchCurrentUser()
      set({ user, status: 'authenticated', error: null })
      return true
    } catch {
      clearToken()
      set({ user: null, status: 'unauthenticated', error: null })
      return false
    }
  },
}))
