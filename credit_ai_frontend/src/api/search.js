import { authFetch } from '@/api/client'

const SEARCH_BASE = '/api/search/search_company'

export async function searchCompanies(query, limit = 25) {
  const filters = encodeURIComponent(
    JSON.stringify({
      nameStartsWith: query,
      entityType: ['company', 'llp'],
    })
  )

  const response = await authFetch(`${SEARCH_BASE}?limit=${limit}&filters=${filters}`)

  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`)
  }

  const json = await response.json()
  const entities = json?.data?.entities ?? {}

  const companies = (entities.companies ?? []).map((c) => ({
    id: c.cin,
    cin: c.cin,
    legalName: c.legal_name,
    status: c.status,
    type: 'company',
    bid: c.bid,
  }))

  const llps = (entities.llps ?? []).map((l) => ({
    id: l.llpin,
    cin: l.llpin,
    legalName: l.legal_name,
    status: l.status,
    type: 'llp',
    bid: l.bid,
  }))

  const seen = new Set()
  const results = []
  for (const company of [...companies, ...llps]) {
    if (!company.id || seen.has(company.id)) continue
    seen.add(company.id)
    results.push(company)
  }

  return {
    results,
    totalCount: json?.data?.total_count ?? 0,
    hasMore: json?.data?.has_more ?? false,
  }
}
