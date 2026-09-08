export const THINKING_STAGES = [
  { id: 'fetch', label: 'Loading filings' },
  { id: 'report', label: 'Credit assessment' },
]

export function companyLabel(names) {
  if (!names?.length) return 'the company'
  if (names.length === 1) return names[0]
  return `${names[0]} and ${names.length - 1} other${names.length > 2 ? 's' : ''}`
}

export function thoughtsForStage(stageId, names) {
  const name = companyLabel(names)
  const map = {
    fetch: [
      `Opening the Probe filings packet for ${name}`,
      'Pulling standalone P&L, balance sheet, and cash-flow statements',
      'Reading capital structure, charges, and contingent liabilities',
      'Indexing GST, EPFO, directors, and compliance flags',
      'Waiting until the company packet is complete before writing',
    ],
    report: [
      `Writing the credit assessment for ${name}`,
      'Using filings plus live web search for news and legal context',
      'Anchoring strengths and red flags to specific figures',
      'Drafting tables, trends, and a risk conclusion in one pass',
    ],
  }
  return map[stageId] ?? map.fetch
}

export const SCAN_TOKENS = [
  'Standalone P&L',
  'Debt / equity',
  'Interest coverage',
  'Cash from ops',
  'WC days',
  'MSME delays',
  'Rating outlook',
  'Related parties',
  'Charges',
  'Legal cases',
]

export function isThinStream(text) {
  const trimmed = (text ?? '').trim()
  if (!trimmed) return true
  const lines = trimmed.split('\n').map((line) => line.trim()).filter(Boolean)
  const body = trimmed
    .replace(/^#+\s.*$/gm, '')
    .replace(/^CIN\b.*$/gim, '')
    .replace(/^\([^)]*CIN[^)]*\)\s*$/gim, '')
    .trim()
  if (trimmed.length < 480 || body.length < 280) return true
  if (lines.length <= 6 && lines.every((line) => line.startsWith('#') || /^CIN\b/i.test(line) || line.length < 90)) {
    return true
  }
  return false
}
