import { useState } from 'react'
import { Paperclip, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PeerPicker } from '@/components/PeerPicker'

export function ComposerExtras({
  disabled = false,
  extraPeers = [],
  extraSearches = '',
  files = [],
  excludeCins = [],
  onPeersChange,
  onSearchesChange,
  onFilesChange,
}) {
  const [open, setOpen] = useState(false)
  const extraCount =
    extraPeers.length +
    (extraSearches.trim() ? extraSearches.trim().split('\n').filter(Boolean).length : 0) +
    files.length

  return (
    <div className="mt-2">
      <div className="flex flex-wrap items-center gap-1">
        <Button
          type="button"
          variant={open ? 'secondary' : 'ghost'}
          size="sm"
          className="h-7 gap-1 px-2 text-xs"
          disabled={disabled}
          onClick={() => setOpen((value) => !value)}
        >
          <Users className="h-3.5 w-3.5" />
          Peers & docs
          {extraCount > 0 ? ` (${extraCount})` : ''}
        </Button>
      </div>
      {open && (
        <div className="mt-2 space-y-3 rounded-xl border border-border/50 bg-card/40 p-3">
          <div>
            <p className="mb-1 text-[11px] font-medium text-foreground">Extra peers</p>
            <PeerPicker
              peers={extraPeers}
              onChange={onPeersChange}
              disabled={disabled}
              excludeCins={excludeCins}
            />
            <p className="mt-1 text-[10px] text-muted-foreground">
              Fetched from Probe like the borrower. You can also add peers from Show charts.
            </p>
          </div>
          <label className="block text-[11px] font-medium text-foreground">
            Extra web searches
            <textarea
              className="mt-1 min-h-[56px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
              placeholder={'cigarette tax India\nFMCG volume outlook'}
              value={extraSearches}
              onChange={(event) => onSearchesChange(event.target.value)}
              disabled={disabled}
            />
          </label>
          <label className="block text-[11px] font-medium text-foreground">
            <span className="mb-1 inline-flex items-center gap-1">
              <Paperclip className="h-3 w-3" />
              Documents
            </span>
            <Input
              className="mt-1 cursor-pointer"
              type="file"
              multiple
              accept=".csv,.xlsx,.docx,.txt,.md"
              disabled={disabled}
              onChange={(event) => onFilesChange(Array.from(event.target.files || []).slice(0, 6))}
            />
            <span className="mt-1 block font-normal text-[10px] text-muted-foreground">
              CSV, Excel, Word, or text. Up to 6 files, 2.5 MB each.
            </span>
            {files.length > 0 && (
              <span className="mt-1 block font-normal text-foreground/80">
                {files.map((file) => file.name).join(', ')}
              </span>
            )}
          </label>
        </div>
      )}
    </div>
  )
}
