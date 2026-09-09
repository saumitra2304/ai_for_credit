import { describe, expect, it } from 'vitest'
import { formatInrCompact } from './formatMoney.js'
import { formatChatMarkdown } from './formatChatMarkdown.js'

describe('formatInrCompact', () => {
  it('expresses crore-scale amounts in rupees crore with Indian grouping', () => {
    expect(formatInrCompact(1_234_567_890)).toBe('₹123.46 crore')
  })

  it('expresses lakh-scale amounts in rupees lakh', () => {
    expect(formatInrCompact(5_000_000)).toBe('₹50 lakh')
  })

  it('groups smaller rupee amounts with Indian commas', () => {
    expect(formatInrCompact(50_000)).toBe('₹50,000')
  })
})

describe('formatChatMarkdown', () => {
  it('strips a unicode bullet after a markdown list marker', () => {
    expect(formatChatMarkdown('- • Strength one')).toBe('- Strength one')
  })

  it('turns a leading unicode bullet into a markdown list item', () => {
    expect(formatChatMarkdown('• Red flag')).toBe('- Red flag')
  })

  it('converts million-rupee figures into crore with grouping', () => {
    expect(formatChatMarkdown('Revenue of 1234.56 million')).toBe(
      'Revenue of ₹123.46 crore'
    )
  })

  it('converts billion figures into crore', () => {
    expect(formatChatMarkdown('Debt of 1.5 billion')).toBe('Debt of ₹150 crore')
  })

  it('formats already-crore figures with a rupee sign and grouping', () => {
    expect(formatChatMarkdown('PAT 1234.5 crore')).toBe('PAT ₹1,234.5 crore')
  })

  it('formats bare 7+ digit rupee amounts in tables', () => {
    expect(formatChatMarkdown('| 1234567890 |')).toBe('| ₹123.46 crore |')
  })

  it('leaves years, CINs, and percentages unchanged', () => {
    const source = 'FY 2024 CIN L74120MH1985PLC035308 margin 12.5%'
    expect(formatChatMarkdown(source)).toBe(source)
  })

  it('does not treat share counts as money', () => {
    expect(formatChatMarkdown('issued 2 million shares')).toBe(
      'issued 2 million shares'
    )
  })

  it('does not rewrite fenced code', () => {
    const source = '```\n1234567890\n```'
    expect(formatChatMarkdown(source)).toBe(source)
  })

  it('does not rewrite inline code', () => {
    expect(formatChatMarkdown('use `1234567890` as id')).toBe('use `1234567890` as id')
  })
})
