const CRORE = 10_000_000
const LAKH = 100_000

function formatScalar(value, maxFractionDigits = 2) {
  return value.toLocaleString('en-IN', {
    maximumFractionDigits: maxFractionDigits,
    minimumFractionDigits: 0,
  })
}

export function formatGroupedNumber(value, maxFractionDigits = 1) {
  if (value == null || value === '' || Number.isNaN(Number(value))) return '—'
  return Number(value).toLocaleString('en-IN', {
    maximumFractionDigits: maxFractionDigits,
    minimumFractionDigits: 0,
  })
}

export function formatInrCompact(value) {
  if (value == null || value === '' || Number.isNaN(Number(value))) return '—'
  const n = Number(value)
  const abs = Math.abs(n)
  const sign = n < 0 ? '-' : ''
  if (abs >= CRORE) {
    return `${sign}₹${formatScalar(abs / CRORE)} crore`
  }
  if (abs >= LAKH) {
    return `${sign}₹${formatScalar(abs / LAKH)} lakh`
  }
  return `${sign}₹${formatScalar(abs)}`
}

export function unitToRupees(unit) {
  const u = String(unit).toLowerCase()
  if (u.startsWith('billion') || u === 'bn') return 1_000_000_000
  if (u.startsWith('million') || u === 'mn') return 1_000_000
  if (u.startsWith('crore') || u.startsWith('cr')) return CRORE
  if (u.startsWith('lakh') || u.startsWith('lac')) return LAKH
  return 1
}
