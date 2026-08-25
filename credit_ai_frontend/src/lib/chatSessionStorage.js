const STORAGE_KEY = 'credit-ai-active-session'

export function saveChatSession(session) {
  try {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        ...session,
        savedAt: Date.now(),
      })
    )
  } catch {
    // Ignore quota errors.
  }
}

export function loadChatSession() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function clearChatSession() {
  sessionStorage.removeItem(STORAGE_KEY)
}

export function getInitialAppState() {
  const saved = loadChatSession()
  if (!saved) {
    return {
      activeChatId: null,
      selectedCompanies: [],
      initialMessages: [],
      recovered: false,
    }
  }

  return {
    activeChatId: saved.activeChatId ?? null,
    selectedCompanies: saved.selectedCompanies ?? [],
    initialMessages: saved.messages ?? [],
    recovered: Boolean(saved.interrupted),
  }
}
