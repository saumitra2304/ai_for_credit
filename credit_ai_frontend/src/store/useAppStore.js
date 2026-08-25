import { create } from 'zustand'
import { newChatId } from '@/lib/chatId'
import { clearChatSession, getInitialAppState } from '@/lib/chatSessionStorage'

const initial = getInitialAppState()

export const useAppStore = create((set, get) => ({
  activeChatId: initial.activeChatId,
  selectedCompanies: initial.selectedCompanies,
  messages: initial.initialMessages,
  sessionKey: 0,
  historyVersion: 0,
  recoveredNotice: initial.recovered,
  sidebarTab: 'search',

  setSidebarTab: (sidebarTab) => set({ sidebarTab }),

  dismissRecovered: () => set({ recoveredNotice: false }),

  selectCompany: (company) =>
    set((state) => {
      if (state.selectedCompanies.some((c) => c.id === company.id)) return state
      return { selectedCompanies: [...state.selectedCompanies, company] }
    }),

  removeCompany: (id) =>
    set((state) => ({
      selectedCompanies: state.selectedCompanies.filter((c) => c.id !== id),
    })),

  clearCompanies: () => set({ selectedCompanies: [] }),

  setMessages: (messages) => set({ messages }),

  updateMessages: (updater) =>
    set((state) => ({
      messages: typeof updater === 'function' ? updater(state.messages) : updater,
    })),

  ensureChatId: () => {
    const { activeChatId } = get()
    if (activeChatId != null) return activeChatId
    const id = newChatId()
    set({ activeChatId: id })
    return id
  },

  startNewChat: () => {
    clearChatSession()
    set((state) => ({
      recoveredNotice: false,
      activeChatId: newChatId(),
      messages: [],
      selectedCompanies: [],
      sessionKey: state.sessionKey + 1,
    }))
  },

  loadSession: (session) => {
    clearChatSession()
    set((state) => ({
      recoveredNotice: false,
      activeChatId: session.chatId,
      selectedCompanies: session.companies,
      messages: session.messages,
      sessionKey: state.sessionKey + 1,
    }))
  },

  resetChat: () => {
    clearChatSession()
    set((state) => ({
      recoveredNotice: false,
      activeChatId: newChatId(),
      messages: [],
      sessionKey: state.sessionKey + 1,
    }))
  },

  completeChat: () =>
    set((state) => ({
      recoveredNotice: false,
      historyVersion: state.historyVersion + 1,
    })),

  mergeServerSession: (session) => {
    const state = get()
    if (!session?.messages?.length) return
    if (session.messages.length > state.messages.length) {
      set({
        messages: session.messages,
        selectedCompanies: session.companies,
        recoveredNotice: false,
      })
    }
  },
}))
