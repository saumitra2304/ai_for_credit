import { useCallback, useEffect, useMemo, useState } from 'react'
import { Search, X } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { searchCompanies } from '@/api/search'
import { debounce } from '@/lib/utils'

export function PeerPicker({
  peers = [],
  onChange,
  disabled = false,
  excludeCins = [],
  placeholder = 'Search a peer by name or CIN',
}) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const blocked = useMemo(() => {
    const ids = new Set(peers.map((peer) => String(peer.cin || '').toUpperCase()))
    for (const cin of excludeCins) {
      if (cin) ids.add(String(cin).toUpperCase())
    }
    return ids
  }, [peers, excludeCins])

  const performSearch = useCallback(async (searchQuery) => {
    if (!searchQuery.trim() || searchQuery.trim().length < 2) {
      setResults([])
      return
    }
    setLoading(true)
    try {
      const data = await searchCompanies(searchQuery.trim(), 8)
      setResults(data.results || [])
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  const debouncedSearch = useMemo(() => debounce(performSearch, 300), [performSearch])

  useEffect(() => {
    debouncedSearch(query)
  }, [query, debouncedSearch])

  const addPeer = (company) => {
    const cin = String(company.cin || '').trim().toUpperCase()
    if (!cin || blocked.has(cin) || peers.length >= 8) return
    onChange([
      ...peers,
      {
        cin,
        legalName: company.legalName || cin,
        name: company.legalName || cin,
        source: company.source || 'search',
      },
    ])
    setQuery('')
    setResults([])
  }

  return (
    <div>
      {peers.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1">
          {peers.map((peer) => (
            <Badge key={peer.cin} variant="secondary" className="h-6 gap-1 pr-1 text-[10px] font-normal">
              <span className="max-w-[min(12rem,calc(100vw-8rem))] truncate">{peer.legalName || peer.cin}</span>
              <button
                type="button"
                disabled={disabled}
                onClick={() => onChange(peers.filter((item) => item.cin !== peer.cin))}
                className="rounded-full p-0.5 hover:bg-muted"
              >
                <X className="h-2.5 w-2.5" />
              </button>
            </Badge>
          ))}
        </div>
      )}
      <div className="relative">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className="h-8 pl-8 text-sm"
        />
      </div>
      {loading && <p className="mt-1 text-[10px] text-muted-foreground">Searching…</p>}
      {!loading && results.length > 0 && (
        <div className="mt-1 max-h-36 overflow-y-auto rounded-md border border-border/50">
          {results.map((company) => {
            const taken = blocked.has(String(company.cin || '').toUpperCase())
            return (
              <button
                key={company.id || company.cin}
                type="button"
                disabled={disabled || taken}
                onClick={() => addPeer(company)}
                className="flex w-full items-start justify-between gap-2 border-b border-border/40 px-2.5 py-1.5 text-left last:border-b-0 hover:bg-muted/40 disabled:opacity-40"
              >
                <span className="min-w-0">
                  <span className="block truncate text-xs font-medium">{company.legalName}</span>
                  <span className="font-mono text-[10px] text-muted-foreground">{company.cin}</span>
                </span>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
