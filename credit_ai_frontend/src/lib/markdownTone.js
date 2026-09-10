export function nodeText(node) {
  if (node == null || typeof node === 'boolean') return ''
  if (typeof node === 'string' || typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(nodeText).join('')
  if (node?.props?.children) return nodeText(node.props.children)
  return ''
}

export function headingTone(children) {
  const text = nodeText(children).toLowerCase()
  if (/red flag|watch item|\brisks?\b|decline|caution|litigation|nclt/.test(text)) {
    if (/strength/.test(text) && /red flag/.test(text)) return ''
    return 'risk'
  }
  if (/strength/.test(text)) return 'strength'
  if (/recommend/.test(text)) return 'recommend'
  return ''
}

export function cellTone(children) {
  const text = nodeText(children).trim()
  if (!text || /^[—–-]+$/.test(text)) return 'muted'
  const compact = text.replace(/,/g, '').replace(/^rs\.?\s*/i, '')
  if (/^-\d/.test(compact)) return 'neg'
  return ''
}

export function calloutTone(children) {
  const text = nodeText(children).trim()
  if (/^(advance|approved?)\b/i.test(text)) return 'advance'
  if (/^(caution|watch)\b/i.test(text)) return 'caution'
  if (/^(decline|reject)/i.test(text)) return 'decline'
  return ''
}
