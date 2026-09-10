import { useEffect, useMemo, useState } from 'react'
import { Loader2, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PeerPicker } from '@/components/PeerPicker'
import { fetchCompanyDetails } from '@/api/companyDetails'
import { extractChartData } from '@/lib/chartData'
import { extraCinsText, suggestedPeersFromCharts } from '@/lib/peerSelect'

export function MemoComposer({
  open,
  loading,
  onClose,
  onGenerate,
  selectedCompanies = [],
}) {
  const [notes, setNotes] = useState('')
  const [extraSearches, setExtraSearches] = useState('')
  const [includeChat, setIncludeChat] = useState(true)
  const [includeProbePeers, setIncludeProbePeers] = useState(true)
  const [files, setFiles] = useState([])
  const [suggested, setSuggested] = useState([])
  const [selectedPeers, setSelectedPeers] = useState([])
  const [manualPeers, setManualPeers] = useState([])
  const [suggesting, setSuggesting] = useState(false)

  const excludeCins = useMemo(
    () => selectedCompanies.map((company) => company.cin).filter(Boolean),
    [selectedCompanies]
  )

  useEffect(() => {
    if (!open) return
    const onKey = (event) => {
      if (event.key === 'Escape' && !loading) onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, loading, onClose])

  useEffect(() => {
    if (!open) return
    setNotes('')
    setExtraSearches('')
    setIncludeChat(true)
    setIncludeProbePeers(true)
    setFiles([])
    setManualPeers([])
    setSuggested([])
    setSelectedPeers([])
    if (excludeCins.length === 0) return undefined
    const controller = new AbortController()
    setSuggesting(true)
    Promise.all(
      excludeCins.map((cin) =>
        fetchCompanyDetails(cin, controller.signal).catch((err) => {
          if (err?.name === 'AbortError') throw err
          return null
        })
      )
    )
      .then((payloads) => {
        const peers = suggestedPeersFromCharts(
          payloads.filter(Boolean).map((payload) => extractChartData(payload)),
          { excludeCins, limit: 3 }
        )
        setSuggested(peers)
        setSelectedPeers(peers)
      })
      .catch((err) => {
        if (err?.name === 'AbortError') return
        setSuggested([])
        setSelectedPeers([])
      })
      .finally(() => setSuggesting(false))
    return () => controller.abort()
  }, [open, excludeCins])

  if (!open) return null

  const extraPeers = includeProbePeers
    ? [
        ...selectedPeers,
        ...manualPeers.filter((peer) => !selectedPeers.some((item) => item.cin === peer.cin)),
      ]
    : manualPeers

  const payload = {
    notes,
    extraCins: extraCinsText(extraPeers),
    extraSearches,
    includeChat,
    autoPeers: includeProbePeers && extraPeers.length === 0,
    files,
  }

  const toggleSuggested = (peer) => {
    setSelectedPeers((current) =>
      current.some((item) => item.cin === peer.cin)
        ? current.filter((item) => item.cin !== peer.cin)
        : [...current, peer]
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center overflow-y-auto bg-background/70 p-0 backdrop-blur-sm sm:items-start sm:p-4 sm:pt-[8vh]">
      <div className="glass-panel w-full max-h-[96dvh] overflow-y-auto rounded-t-2xl p-4 pb-[max(1rem,env(safe-area-inset-bottom))] shadow-lg sm:max-w-lg sm:rounded-xl sm:p-5">
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-foreground">Credit committee memo</h2>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              Filings already in this chat are included. Add peers, searches, the conversation, or your own Excel / Word files.
            </p>
          </div>
          <Button type="button" variant="ghost" size="icon" className="h-7 w-7" onClick={onClose} disabled={loading}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <label className="mb-3 block text-xs font-medium text-foreground">
          Officer notes / facility / what to add
          <textarea
            className="mt-1 min-h-[88px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm leading-relaxed outline-none focus-visible:ring-2 focus-visible:ring-ring"
            placeholder="e.g. 12-month WC of Rs 500 crore, first ranking charge. Add Godfrey Phillips as a peer. Stress CCC +20 days."
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            maxLength={4000}
            disabled={loading}
          />
        </label>

        <label className="mb-3 flex items-start gap-2 text-xs text-foreground">
          <input
            type="checkbox"
            className="mt-0.5"
            checked={includeProbePeers}
            onChange={(event) => setIncludeProbePeers(event.target.checked)}
            disabled={loading}
          />
          <span>
            Include top Probe peers by revenue
            <span className="mt-0.5 block font-normal text-muted-foreground">
              Same ranking as Show charts → Peer revenue. Names without a CIN are skipped.
            </span>
          </span>
        </label>

        {includeProbePeers && (
          <div className="mb-3 rounded-md border border-border/50 p-2">
            {suggesting && (
              <p className="text-[11px] text-muted-foreground">Loading peer revenue comps…</p>
            )}
            {!suggesting && suggested.length === 0 && (
              <p className="text-[11px] text-muted-foreground">
                No peer CINs on the Probe peer-revenue list. Search below to add comps.
              </p>
            )}
            {suggested.map((peer) => (
              <label key={peer.cin} className="flex items-start gap-2 py-1 text-xs">
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={selectedPeers.some((item) => item.cin === peer.cin)}
                  onChange={() => toggleSuggested(peer)}
                  disabled={loading}
                />
                <span>
                  <span className="font-medium">{peer.legalName}</span>
                  <span className="mt-0.5 block font-mono text-[10px] text-muted-foreground">{peer.cin}</span>
                </span>
              </label>
            ))}
          </div>
        )}

        <div className="mb-3">
          <p className="mb-1 text-xs font-medium text-foreground">More peers</p>
          <PeerPicker
            peers={manualPeers}
            onChange={setManualPeers}
            disabled={loading}
            excludeCins={[...excludeCins, ...selectedPeers.map((peer) => peer.cin)]}
          />
        </div>

        <label className="mb-3 block text-xs font-medium text-foreground">
          Extra web searches
          <textarea
            className="mt-1 min-h-[64px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm leading-relaxed outline-none focus-visible:ring-2 focus-visible:ring-ring"
            placeholder={'ITC cigarette tax\nFMCG volume India\nrepo rate outlook'}
            value={extraSearches}
            onChange={(event) => setExtraSearches(event.target.value)}
            disabled={loading}
          />
          <span className="mt-1 block font-normal text-muted-foreground">
            One topic per line. Used for sector / macro / ratings follow-ups. Cited, not invented.
          </span>
        </label>

        <label className="mb-3 flex items-start gap-2 text-xs text-foreground">
          <input
            type="checkbox"
            className="mt-0.5"
            checked={includeChat}
            onChange={(event) => setIncludeChat(event.target.checked)}
            disabled={loading}
          />
          <span>
            Include this chat
            <span className="mt-0.5 block font-normal text-muted-foreground">
              Officer questions and Kuber answers are passed into the memo packet.
            </span>
          </span>
        </label>

        <label className="mb-4 block text-xs font-medium text-foreground">
          Your documents
          <Input
            className="mt-1 cursor-pointer"
            type="file"
            multiple
            accept=".csv,.xlsx,.docx,.txt,.md"
            disabled={loading}
            onChange={(event) => setFiles(Array.from(event.target.files || []).slice(0, 6))}
          />
          <span className="mt-1 block font-normal text-muted-foreground">
            CSV, Excel (.xlsx), Word (.docx), or text. Up to 6 files, 2.5 MB each.
          </span>
          {files.length > 0 && (
            <span className="mt-1 block font-normal text-foreground/80">
              {files.map((file) => file.name).join(', ')}
            </span>
          )}
        </label>

        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button type="button" variant="outline" size="sm" className="w-full sm:w-auto" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="button" variant="outline" size="sm" className="w-full sm:w-auto" disabled={loading} onClick={() => onGenerate('docx', payload)}>
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
            Word
          </Button>
          <Button type="button" size="sm" className="w-full sm:w-auto" disabled={loading} onClick={() => onGenerate('pdf', payload)}>
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
            PDF
          </Button>
        </div>
      </div>
    </div>
  )
}
