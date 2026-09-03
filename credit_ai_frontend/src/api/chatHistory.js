import { authJson } from '@/api/client'

const CHAT_HISTORY_BASE = '/api/chat_history'

export async function fetchChatHistory() {
  return authJson(CHAT_HISTORY_BASE)
}

export async function fetchChatSession(chatId) {
  if (!chatId) return null
  const session = await authJson(`${CHAT_HISTORY_BASE}/${encodeURIComponent(chatId)}`)
  return session ? parseChatSession(session) : null
}

export function companyCacheToCompanies(companyCache) {
  if (!companyCache) return []

  return Object.entries(companyCache).map(([cin, entry]) => ({
    id: cin,
    cin,
    legalName: entry?.label ?? entry?.detail?.company?.legal_name ?? cin,
    status: entry?.detail?.company?.status ?? 'Unknown',
    type: 'company',
  }))
}

function resolveCompanies(session) {
  const fromCache = companyCacheToCompanies(session.company_cache)
  if (fromCache.length > 0) return fromCache
  return smeDataToCompanies(session.sme_data)
}

export function smeDataToCompanies(smeData) {
  if (!smeData) return []

  return Object.entries(smeData).map(([cin, entry]) => {
    const company = entry?.data?.company ?? {}
    return {
      id: cin,
      cin,
      legalName: company.legal_name ?? cin,
      status: company.status ?? 'Unknown',
      type: 'company',
    }
  })
}

export function messageTrailToMessages(trail, chatId) {
  if (!trail?.length) return []

  const messages = []
  trail.forEach((item, index) => {
    const turnId = `${chatId}-turn-${index}`
    messages.push({
      id: `${chatId}-user-${index}`,
      role: 'user',
      content: item.query,
      turnId,
    })
    messages.push({
      id: `${chatId}-assistant-${index}`,
      role: 'assistant',
      content: item.response,
      turnId,
    })
  })

  return messages
}

export function parseChatSession(session) {
  const trail = session.message_trail ?? []
  const companies = resolveCompanies(session)
  const preview =
    session.preview || trail[trail.length - 1]?.query || trail[0]?.query || 'Empty conversation'

  return {
    chatId: session.chat_id,
    preview,
    messageCount: session.message_count ?? trail.length,
    companies,
    messages: messageTrailToMessages(trail, session.chat_id),
    updatedAt: session.updated_at ?? (trail.length > 0 ? trail[trail.length - 1]?.query : null),
  }
}
