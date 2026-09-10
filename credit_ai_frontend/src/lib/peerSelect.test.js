import { describe, expect, it } from 'vitest'
import { extractChartData } from '@/lib/chartData'
import { selectPeerCins, suggestedPeers } from '@/lib/peerSelect'

const BORROWER = 'L16005WB1910PLC001985'

function payload() {
  return {
    data: {
      company: { legal_name: 'ITC Limited', cin: BORROWER },
      financials: [],
      peer_comparison: [
        {
          peers: [
            { legalName: 'Indian Potash Limited', revenue: 500_000_000_000 },
            {
              legalName: 'Godfrey Phillips India Limited',
              cin: 'L16004MH1936PLC008587',
              revenue: 40_000_000_000,
            },
            { legalName: 'ITC Limited', cin: BORROWER, revenue: 90_000_000_000 },
            {
              legalName: 'VST Industries Limited',
              cin: 'L29150TG1930PLC000576',
              revenue: 15_000_000_000,
            },
          ],
        },
      ],
    },
  }
}

describe('suggestedPeers from Probe peer revenue', () => {
  it('keeps CIN on chart peers and ranks extra comps by revenue', () => {
    const charts = extractChartData(payload())
    expect(charts.peers.map((row) => row.cin)).toContain('L16004MH1936PLC008587')
    const peers = suggestedPeers(charts, { excludeCins: [BORROWER], limit: 3 })
    expect(peers.map((row) => row.cin)).toEqual([
      'L16004MH1936PLC008587',
      'L29150TG1930PLC000576',
    ])
    expect(selectPeerCins(charts, { excludeCins: [BORROWER], limit: 1 })).toEqual([
      'L16004MH1936PLC008587',
    ])
  })
})
