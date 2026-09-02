function yearLabel(value) {
  if (!value) return ''
  const text = String(value)
  const match = text.match(/^(\d{4})/)
  return match ? match[1] : text
}

function num(value) {
  if (value == null || value === '') return null
  const n = Number(value)
  return Number.isFinite(n) ? n : null
}

function standaloneYears(financials) {
  return (financials ?? [])
    .filter((row) => (row.nature ?? 'STANDALONE') === 'STANDALONE')
    .sort((a, b) => String(a.year).localeCompare(String(b.year)))
}

export function crore(value) {
  if (value == null) return null
  return Number((value / 10_000_000).toFixed(2))
}

export function formatCrore(value) {
  if (value == null) return '—'
  return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 1 })} cr`
}

export function formatInr(value) {
  if (value == null) return '—'
  return `₹${Number(value).toLocaleString('en-IN')}`
}

function countBy(items, key) {
  const counts = {}
  for (const item of items ?? []) {
    const label = item?.[key] || 'Unknown'
    counts[label] = (counts[label] ?? 0) + 1
  }
  return Object.entries(counts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
}

export function extractChartData(payload) {
  const data = payload?.data ?? payload ?? {}
  const company = data.company ?? {}
  const financials = standaloneYears(data.financials)

  const pnl = financials.map((row) => {
    const items = row.pnl?.lineItems ?? {}
    return {
      year: yearLabel(row.year),
      revenue: crore(items.net_revenue),
      operatingProfit: crore(items.operating_profit),
      pat: crore(items.profit_after_tax),
      ebit: crore(items.profit_before_interest_and_tax),
    }
  })

  const ratios = financials.map((row) => {
    const r = row.ratios ?? {}
    return {
      year: yearLabel(row.year),
      ebitdaMargin: num(r.ebitda_margin),
      netMargin: num(r.net_margin),
      roe: num(r.return_on_equity),
      roce: num(r.return_on_capital_employed),
      currentRatio: num(r.current_ratio),
      debtEquity: num(r.debt_by_equity),
      interestCover: num(r.interest_coverage_ratio),
    }
  })

  const workingCapital = financials.map((row) => {
    const r = row.ratios ?? {}
    return {
      year: yearLabel(row.year),
      inventoryDays: num(r.inventory_by_sales_days),
      debtorDays: num(r.debtors_by_sales_days),
      payableDays: num(r.payables_by_sales_days),
      ccc: num(r.cash_conversion_cycle),
    }
  })

  const balanceSheet = financials.map((row) => {
    const sub = row.bs?.subTotals ?? {}
    return {
      year: yearLabel(row.year),
      equity: crore(sub.total_equity),
      debt: crore(sub.total_debt),
      currentAssets: crore(sub.total_current_assets),
      currentLiabilities: crore(sub.total_current_liabilities),
    }
  })

  const cashFlow = financials.map((row) => {
    const cf = row.cash_flow ?? {}
    return {
      year: yearLabel(row.year),
      operating: crore(cf.cash_flows_from_used_in_operating_activities),
      investing: crore(cf.cash_flows_from_used_in_investing_activities),
      financing: crore(cf.cash_flows_from_used_in_financing_activities),
    }
  })

  const score = data.probe_financial_score ?? {}
  const probeScores = [
    { name: 'Overall', value: num(score.overall_financial_score) },
    { name: 'Growth', value: num(score.growth_score) },
    { name: 'Profitability', value: num(score.profitability_score) },
    { name: 'Liquidity', value: num(score.liquidity_score) },
    { name: 'Solvency', value: num(score.solvency_score) },
    { name: 'Efficiency', value: num(score.efficiency_score) },
  ].filter((row) => row.value != null)

  const peerBlock = (data.peer_comparison ?? [])[0] ?? {}
  const peers = (peerBlock.peers ?? [])
    .map((peer) => ({
      name: (peer.legalName ?? peer.legal_name ?? 'Peer').replace(/ PRIVATE LIMITED| LIMITED/gi, ''),
      revenue: crore(peer.revenue),
    }))
    .filter((row) => row.revenue != null)
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, 8)

  const bench = (peerBlock.benchMarks ?? [])[0] ?? {}
  const peerBench = [
    { metric: 'Net margin', company: num(bench.net_margin), median: num(bench.median_net_margin) },
    { metric: 'EBITDA margin', company: num(bench.ebitda_margin), median: num(bench.median_ebitda_margin) },
    { metric: 'ROE', company: num(bench.return_on_equity), median: num(bench.median_return_on_equity) },
    { metric: 'ROCE', company: num(bench.return_on_capital_employed), median: num(bench.median_return_on_capital_employed) },
    { metric: 'Current ratio', company: num(bench.current_ratio), median: num(bench.median_current_ratio) },
  ].filter((row) => row.company != null || row.median != null)

  const msme = data.msme_supplier_payment_delays ?? {}
  const msmeTrend = (msme.trend ?? []).map((row) => ({
    period: String(row.period ?? '').replace(' to ', '\n'),
    amount: crore(row.amount),
  }))
  const msmeSuppliers = (msme.delays_for_period?.delays ?? [])
    .map((row) => ({
      name: row.supplier_name,
      amount: crore(row.amount_due),
    }))
    .sort((a, b) => (b.amount ?? 0) - (a.amount ?? 0))
    .slice(0, 8)

  const latestRpt = [...(data.related_party_transactions ?? [])].sort((a, b) =>
    String(b.financial_year).localeCompare(String(a.financial_year))
  )[0]
  const relatedParties = (latestRpt?.company ?? [])
    .map((row) => ({
      name: (row.legal_name ?? row.name ?? 'Party').slice(0, 42),
      amount: crore(row.amount),
      type: row.type_of_transaction,
    }))
    .filter((row) => row.amount != null)
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 10)

  const holdersYear = [...(data.shareholdings_more_than_five_percent ?? [])].sort((a, b) =>
    String(b.financial_year).localeCompare(String(a.financial_year))
  )[0]
  const shareholders = ['company', 'llp', 'individual', 'others'].flatMap((bucket) =>
    (holdersYear?.[bucket] ?? []).map((row) => ({
      name: (row.name ?? 'Holder').slice(0, 40),
      value: num(row.shareholding_percentage),
    }))
  ).filter((row) => row.value != null && row.value > 0)

  const legalByStatus = countBy(data.legal_history, 'case_status')
  const legalBySeverity = countBy(data.legal_history, 'severity')

  const leverage = ratios.map((row) => ({
    year: row.year,
    debtEquity: row.debtEquity,
    interestCover: row.interestCover,
  })).filter((row) => row.debtEquity != null || row.interestCover != null)

  const liquidity = financials.map((row) => {
    const r = row.ratios ?? {}
    const sub = row.bs?.subTotals ?? {}
    return {
      year: yearLabel(row.year),
      currentRatio: num(r.current_ratio),
      quickRatio: num(r.quick_ratio),
      currentAssets: crore(sub.total_current_assets),
      currentLiabilities: crore(sub.total_current_liabilities),
    }
  })

  const growth = pnl.slice(1).map((row, index) => {
    const prev = pnl[index]
    const pct = (cur, last) =>
      last && last !== 0 && cur != null
        ? Number((((cur - last) / Math.abs(last)) * 100).toFixed(1))
        : null
    return {
      year: row.year,
      revenue: pct(row.revenue, prev.revenue),
      pat: pct(row.pat, prev.pat),
      operatingProfit: pct(row.operatingProfit, prev.operatingProfit),
    }
  })

  const gstByStatus = countBy(data.gst_details, 'status')
  const gstByState = countBy(data.gst_details, 'state').slice(0, 8)
  const gstTimeliness = countBy(data.gst_details, 'filing_timeliness')

  return {
    companyName: company.legal_name ?? 'Company',
    cin: company.cin,
    pnl,
    ratios,
    workingCapital,
    balanceSheet,
    cashFlow,
    leverage,
    liquidity,
    growth,
    probeScores,
    peers,
    peerBench,
    msmeTrend,
    msmeSuppliers,
    relatedParties,
    shareholders,
    legalByStatus,
    legalBySeverity,
    gstByStatus,
    gstByState,
    gstTimeliness,
  }
}
