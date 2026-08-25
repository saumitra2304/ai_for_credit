export function groupMessagesIntoTurns(messages) {
  const turns = []

  for (let i = 0; i < messages.length; i += 1) {
    const msg = messages[i]

    if (msg.role === 'user') {
      const next = messages[i + 1]
      const assistant = next?.role === 'assistant' ? next : null
      turns.push({ user: msg, assistant })
      if (assistant) i += 1
      continue
    }

    turns.push({ user: null, assistant: msg })
  }

  return turns
}

export function createMessage(role, content, turnId) {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    turnId: turnId ?? crypto.randomUUID(),
  }
}

export function createTurnMessages(query) {
  const turnId = crypto.randomUUID()
  return {
    turnId,
    userMessage: createMessage('user', query, turnId),
    assistantId: crypto.randomUUID(),
  }
}
