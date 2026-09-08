export function friendlyAuthMessage(raw, status) {
  if (raw instanceof Error) {
    if (raw.name === 'UnauthorizedError' || status === 401) {
      return 'Email or password is incorrect.'
    }
    raw = raw.message
    status = status ?? raw.status
  }

  if (Array.isArray(raw)) {
    const parts = raw
      .map((item) => (typeof item === 'string' ? item : item?.msg || item?.message || ''))
      .filter(Boolean)
    raw = parts.join(' ')
  } else if (raw && typeof raw === 'object') {
    raw = raw.detail ?? raw.message ?? JSON.stringify(raw)
    if (Array.isArray(raw)) {
      return friendlyAuthMessage(raw, status)
    }
  }

  const text = String(raw || '').trim()
  const lower = text.toLowerCase()

  if (!text || lower === 'unauthorized' || lower === 'failed to fetch' || lower.includes('networkerror')) {
    if (status === 401) return 'Email or password is incorrect.'
    if (status === 409) return 'An account with this email already exists.'
    if (status === 403) return 'New accounts cannot be created right now.'
    if (status === 422) return 'Please check the form and try again.'
    if (!text || lower.includes('fetch') || lower.includes('network')) {
      return 'Could not reach the server. Check your connection and try again.'
    }
  }

  if (lower.includes('string should have at least 8') || lower.includes('min_length')) {
    return 'Password must be at least 8 characters.'
  }
  if (lower.includes('value is not a valid email') || lower.includes('not a valid email')) {
    return 'Enter a valid email address.'
  }
  if (status === 429 || lower.includes('too many attempts')) {
    return 'Too many attempts. Wait a few minutes and try again.'
  }
  if (status === 401 || lower.includes('invalid email or password')) {
    return 'Email or password is incorrect.'
  }
  if (lower.includes('admin access required')) {
    return 'You do not have access to that page.'
  }
  if (status === 403 || lower.includes('registration is disabled') || lower.includes('cannot be created')) {
    return 'New accounts cannot be created right now.'
  }
  if (status === 409 || lower.includes('already exists')) {
    return 'An account with this email already exists.'
  }

  if (text.startsWith('[') || text.startsWith('{')) {
    return 'Please check the form and try again.'
  }

  return text
}
