import { apiUrl, withInternalHeaders } from '@/lib/runtime'

export async function fetchCompanyDetails(cin, signal) {
  const response = await fetch(
    apiUrl(`/api/search/company_details?cin=${encodeURIComponent(cin)}`),
    { headers: withInternalHeaders(), signal }
  )
  if (!response.ok) {
    throw new Error(`Company details failed: ${response.statusText}`)
  }
  return response.json()
}
