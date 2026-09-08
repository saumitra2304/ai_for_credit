import { authFetch } from '@/api/client'

export async function fetchCompanyDetails(cin, signal) {
  const response = await authFetch(
    `/api/search/company_details?cin=${encodeURIComponent(cin)}`,
    { signal }
  )
  if (!response.ok) {
    throw new Error(`Company details failed: ${response.statusText}`)
  }
  return response.json()
}
