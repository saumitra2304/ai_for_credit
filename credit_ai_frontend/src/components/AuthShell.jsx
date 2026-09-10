import { Link } from 'react-router-dom'
import { KuberLogo } from '@/components/KuberLogo'
import { ThemeToggle } from '@/components/ThemeToggle'

export function AuthShell({ children, title, subtitle }) {
  return (
    <div className="grid min-h-dvh lg:grid-cols-2">
      <aside className="relative hidden overflow-hidden bg-[#161D28] px-10 py-10 text-[#F4EFE6] lg:flex lg:flex-col lg:justify-between">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              'radial-gradient(ellipse 60% 45% at 12% 0%, rgba(196,165,116,0.18), transparent), radial-gradient(ellipse 50% 40% at 100% 100%, rgba(244,239,230,0.06), transparent)',
          }}
        />
        <Link to="/" className="relative z-10" aria-label="Kuber home">
          <KuberLogo size={36} showWordmark className="[&_.kuber-wordmark]:text-[#F4EFE6]" />
        </Link>
        <div className="relative z-10 max-w-md">
          <p className="font-display text-4xl leading-tight">
            The filing pack, already read.
          </p>
          <p className="mt-4 text-sm leading-relaxed text-[#F4EFE6]/65">
            Load an Indian company, get a first credit pass, and walk into the committee with a
            memo — not fourteen tabs.
          </p>
        </div>
        <p className="relative z-10 text-xs tracking-wide text-[#C4A574]">
          MCA filings · legal · MSME · cited news · PDF / Word
        </p>
      </aside>

      <div className="relative flex min-h-dvh items-start justify-center overflow-x-hidden overflow-y-auto px-4 pt-[max(3.5rem,calc(env(safe-area-inset-top)+2.75rem))] pb-[max(2rem,env(safe-area-inset-bottom))] sm:items-center sm:px-6 sm:pb-16 sm:pt-16">
        <div className="mesh-bg pointer-events-none absolute inset-0" />
        <div className="absolute right-4 top-[max(1rem,env(safe-area-inset-top))] z-10 flex items-center gap-2">
          <Link to="/" className="text-xs text-muted-foreground hover:text-foreground lg:hidden">
            Home
          </Link>
          <ThemeToggle className="h-8 w-8" />
        </div>
        <div className="relative w-full max-w-md">
          <div className="mb-6 lg:hidden">
            <Link to="/" aria-label="Back to home">
              <KuberLogo size={32} showWordmark />
            </Link>
          </div>
          <h1 className="font-display text-2xl leading-tight sm:text-3xl">{title}</h1>
          <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
          <div className="mt-6 sm:mt-8">{children}</div>
        </div>
      </div>
    </div>
  )
}
