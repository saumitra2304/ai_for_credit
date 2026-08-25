import { useCallback, useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { searchCompanies } from '@/api/search'
import { debounce, cn } from '@/lib/utils'
import { useAppStore } from '@/store/useAppStore'

function getStatusVariant(status) {
  const s = status?.toUpperCase() ?? ''
  if (s === 'ACTIVE') return 'success'
  if (s.includes('STRIKE') || s.includes('DISSOLVED')) return 'destructive'
  return 'warning'
}

export function CompanySearch() {
  const selectedCompanies = useAppStore((s) => s.selectedCompanies)
  const selectCompany = useAppStore((s) => s.selectCompany)
  const removeCompany = useAppStore((s) => s.removeCompany)
  const clearCompanies = useAppStore((s) => s.clearCompanies)

  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [totalCount, setTotalCount] = useState(0)

  const selectedIds = useMemo(
    () => new Set(selectedCompanies.map((c) => c.id)),
    [selectedCompanies]
  )

  const performSearch = useCallback(async (searchQuery) => {
    if (!searchQuery.trim() || searchQuery.trim().length < 2) {
      setResults([])
      setTotalCount(0)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const data = await searchCompanies(searchQuery.trim())
      setResults(data.results)
      setTotalCount(data.totalCount)
    } catch (err) {
      setError(err.message)
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  const debouncedSearch = useMemo(() => debounce(performSearch, 350), [performSearch])

  useEffect(() => {
    debouncedSearch(query)
  }, [query, debouncedSearch])

  return (
    <div className="flex h-full min-h-0 flex-col pt-2">
      <div className="relative px-1 pb-3">
        <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search companies..."
          className="h-8 border-border/50 bg-background/50 pl-8 text-sm"
        />
      </div>

      <AnimatePresence>
        {selectedCompanies.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden px-1 pb-2"
          >
            <div className="flex flex-wrap gap-1">
              {selectedCompanies.map((company) => (
                <Badge
                  key={company.id}
                  variant="secondary"
                  className="h-6 gap-1 pr-1 text-[10px] font-normal"
                >
                  <span className="max-w-[120px] truncate">{company.legalName}</span>
                  <button
                    type="button"
                    onClick={() => removeCompany(company.id)}
                    className="rounded-full p-0.5 hover:bg-muted"
                  >
                    <X className="h-2.5 w-2.5" />
                  </button>
                </Badge>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <ScrollArea className="flex-1 scrollbar-thin">
        <div className="space-y-1 px-1 pb-2">
          {loading &&
            [...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded-lg" />
            ))}

          {!loading && error && (
            <p className="rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive">
              {error}
            </p>
          )}

          {!loading && !error && query.length >= 2 && results.length === 0 && (
            <p className="py-6 text-center text-xs text-muted-foreground">No results</p>
          )}

          {!loading && !error && query.length < 2 && (
            <p className="py-6 text-center text-xs text-muted-foreground">
              Type 2+ characters
            </p>
          )}

          {!loading && results.length > 0 && (
            <>
              <p className="px-1 pb-1 text-[10px] text-muted-foreground">
                {totalCount} found
              </p>
              <AnimatePresence mode="popLayout">
                {results.map((company, i) => {
                  const isSelected = selectedIds.has(company.id)
                  return (
                    <motion.button
                      key={company.id}
                      type="button"
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.03 }}
                      onClick={() => !isSelected && selectCompany(company)}
                      disabled={isSelected}
                      className={cn(
                        'w-full rounded-lg border px-2.5 py-2 text-left transition-all duration-200',
                        isSelected
                          ? 'cursor-default border-primary/20 bg-primary/5 opacity-50'
                          : 'border-border/40 bg-background/30 hover:border-primary/30 hover:bg-background/60'
                      )}
                    >
                      <div className="flex items-start justify-between gap-1.5">
                        <p className="line-clamp-2 text-xs font-medium leading-snug">
                          {company.legalName}
                        </p>
                        <Badge
                          variant={getStatusVariant(company.status)}
                          className="shrink-0 px-1.5 py-0 text-[9px]"
                        >
                          {company.status}
                        </Badge>
                      </div>
                      <p className="mt-1 font-mono text-[10px] text-muted-foreground">
                        {company.cin}
                      </p>
                    </motion.button>
                  )
                })}
              </AnimatePresence>
            </>
          )}
        </div>
      </ScrollArea>

      <div className="border-t border-border/40 p-2">
        <Button
          variant="ghost"
          size="sm"
          className="h-7 w-full text-xs"
          disabled={selectedCompanies.length === 0}
          onClick={clearCompanies}
        >
          Clear all
        </Button>
      </div>
    </div>
  )
}
