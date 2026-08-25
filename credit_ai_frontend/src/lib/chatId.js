export function newChatId() {
  return crypto.randomUUID()
}

export function formatChatIdLabel(chatId) {
  if (chatId == null) return null
  const id = String(chatId)
  if (id.includes('-')) return id.slice(0, 8)
  return id
}
