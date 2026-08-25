import { useEffect } from 'react'
import { fetchChatSession } from '@/api/chatHistory'
import { getInitialAppState } from '@/lib/chatSessionStorage'
import { useAppStore } from '@/store/useAppStore'

const initialState = getInitialAppState()

export function useHydrateSession() {
  const mergeServerSession = useAppStore((s) => s.mergeServerSession)

  useEffect(() => {
    if (!initialState.recovered || !initialState.activeChatId) return

    fetchChatSession(initialState.activeChatId)
      .then(mergeServerSession)
      .catch(() => {})
  }, [mergeServerSession])
}
