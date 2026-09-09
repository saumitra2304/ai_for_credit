import { formatInrCompact, unitToRupees } from './formatMoney.js'

const NON_MONEY_FOLLOW =
  /^\s*(shares?|employees?|people|cases?|customers?|users?|tonnes?|tons?|units?)\b/i

const SCALED_AMOUNT =
  /(?:(?:₹|INR|Rs\.?)\s*)?(\d{1,3}(?:,\d{2,3})+|\d+)(?:\.(\d+))?\s*(billions?|bn|millions?|mn|crores?|crs?|lakhs?|lacs?|cr)\b/gi

const BARE_RUPEES = /(?:(?:₹|INR|Rs\.?)\s*)?(\d{7,})(?:\.(\d+))?(?![\d\w%/])/g

function parseParts(intPart, fracPart) {
  const n = Number(`${String(intPart).replace(/,/g, '')}.${fracPart ?? '0'}`)
  return Number.isFinite(n) ? n : null
}

function sanitizeListLine(line) {
  return line
    .replace(/^(\s*)[•●▪◦‣∙]\s+/, '$1- ')
    .replace(/^(\s*(?:[-*+]|\d+[.)])\s+)(?:[•●▪◦‣∙]\s*)+/, '$1')
}

function formatScaledAmounts(text) {
  return text.replace(SCALED_AMOUNT, (match, intPart, fracPart, unit, offset, full) => {
    const after = full.slice(offset + match.length)
    if (NON_MONEY_FOLLOW.test(after)) return match
    const n = parseParts(intPart, fracPart)
    if (n == null) return match
    return formatInrCompact(n * unitToRupees(unit))
  })
}

function formatBareIntegers(text) {
  return text.replace(BARE_RUPEES, (match, intPart, fracPart, offset, full) => {
    const prev = full[offset - 1]
    if (prev && /[\w.]/.test(prev)) return match
    const n = parseParts(intPart, fracPart)
    if (n == null) return match
    return formatInrCompact(n)
  })
}

function formatProse(text) {
  const sanitized = text.split('\n').map(sanitizeListLine).join('\n')
  return formatBareIntegers(formatScaledAmounts(sanitized))
}

export function formatChatMarkdown(text) {
  if (!text) return text
  return text
    .split(/(```[\s\S]*?```|`[^`]+`)/g)
    .map((part) => (part.startsWith('`') ? part : formatProse(part)))
    .join('')
}
