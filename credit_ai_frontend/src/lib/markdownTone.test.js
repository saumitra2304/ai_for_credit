import { describe, expect, it } from 'vitest'
import { calloutTone, cellTone, headingTone, nodeText } from './markdownTone.js'

describe('markdownTone', () => {
  it('reads nested react children as text', () => {
    expect(nodeText(['Scale', ' ', { props: { children: '& profitability' } }])).toBe(
      'Scale & profitability'
    )
  })

  it('marks red-flag and strength headings', () => {
    expect(headingTone('Red flags / watch items')).toBe('risk')
    expect(headingTone('Strengths')).toBe('strength')
    expect(headingTone('Strengths and Red Flags')).toBe('')
    expect(headingTone('Recommendation and conditions')).toBe('recommend')
    expect(headingTone('Financial position')).toBe('')
  })

  it('marks negative table cells', () => {
    expect(cellTone('-15,694.23')).toBe('neg')
    expect(cellTone('Rs -1,538.38')).toBe('neg')
    expect(cellTone('17,094.97')).toBe('')
    expect(cellTone('—')).toBe('muted')
  })

  it('marks recommendation callouts', () => {
    expect(calloutTone('ADVANCE')).toBe('advance')
    expect(calloutTone('Caution')).toBe('caution')
    expect(calloutTone('Decline')).toBe('decline')
    expect(calloutTone('liquidity')).toBe('')
  })
})
