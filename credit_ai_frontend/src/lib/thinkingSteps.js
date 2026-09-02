export const THINKING_STAGES = [
  { id: 'fetch', label: 'Loading filings' },
  { id: 'credit', label: 'Credit view' },
  { id: 'news', label: 'News scan' },
  { id: 'financials', label: 'Financial detail' },
  { id: 'synthesis', label: 'Synthesis' },
  { id: 'report', label: 'Report' },
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
    credit: [
      `Mapping ratings, CIRP, and distress markers for ${name}`,
      'Checking defaulter lists, MSME delays, and legal history',
      'Weighing rating migration against latest standalone debt',
      'Testing interest coverage against current leverage',
      'Drafting the per-company credit view from those signals',
    ],
    news: [
      `Scanning general, financial, and legal news for ${name}`,
      'Looking for earnings, litigation, and rating headlines',
      'Separating confirmed reports from market noise',
      'Keeping only items that change the credit view',
    ],
    financials: [
      `Walking three-year P&L, balance sheet, and ratios for ${name}`,
      'Tracing revenue, margins, leverage, and working-capital days',
      'Anchoring strengths and red flags to specific figures',
      'Writing the per-company financial detail from the statements',
    ],
    synthesis: [
      'Combining credit, news, and financials into one view',
      'Checking that the conclusion matches the numbers',
      'Resolving contradictions between ratings and cash generation',
      'Finalizing the credit assessment',
    ],
    report: [
      'Formatting tables and the risk conclusion',
      'Finalizing the credit assessment report',
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
