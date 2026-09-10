import { describe, expect, it } from 'vitest'
import { buildChatForm, buildMemoForm, filenameFromDisposition } from '@/api/chat'

describe('filenameFromDisposition', () => {
  it('reads a quoted filename', () => {
    expect(
      filenameFromDisposition(
        'attachment; filename="Acme-Private-Limited-credit-memo.pdf"',
        'fallback.pdf'
      )
    ).toBe('Acme-Private-Limited-credit-memo.pdf')
  })
})

describe('buildMemoForm', () => {
  it('sends revision fields and files as multipart', () => {
    const file = new File(['Metric,1'], 'cma.csv', { type: 'text/csv' })
    const form = buildMemoForm({
      format: 'docx',
      notes: 'WC Rs 500 crore',
      extraCins: 'L16005WB1910PLC001985',
      extraSearches: 'cigarette tax',
      includeChat: false,
      files: [file],
    })
    expect(form.get('format')).toBe('docx')
    expect(form.get('notes')).toBe('WC Rs 500 crore')
    expect(form.get('extra_cins')).toBe('L16005WB1910PLC001985')
    expect(form.get('extra_searches')).toBe('cigarette tax')
    expect(form.get('include_chat')).toBe('false')
    expect(form.get('files')).toBe(file)
    expect(form.get('auto_peers')).toBe('true')
  })
})

describe('buildChatForm', () => {
  it('sends extra peers, searches, and files as multipart', () => {
    const file = new File(['note'], 'note.txt', { type: 'text/plain' })
    const form = buildChatForm({
      cinList: ['L16005WB1910PLC001985'],
      query: 'Compare working capital',
      chatId: 'c1',
      extraCins: 'L16004MH1936PLC008587',
      extraSearches: 'cigarette tax',
      files: [file],
    })
    expect(form.get('cin_list')).toBe('["L16005WB1910PLC001985"]')
    expect(form.get('query')).toBe('Compare working capital')
    expect(form.get('chat_id')).toBe('c1')
    expect(form.get('extra_cins')).toBe('L16004MH1936PLC008587')
    expect(form.get('extra_searches')).toBe('cigarette tax')
    expect(form.get('files')).toBe(file)
  })
})
