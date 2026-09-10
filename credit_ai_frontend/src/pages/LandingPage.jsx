import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  BarChart3,
  FileText,
  Gavel,
  Newspaper,
  Scale,
  Search,
  ShieldCheck,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { KuberLogo } from '@/components/KuberLogo'
import { ThemeToggle } from '@/components/ThemeToggle'
import { useAuthStore } from '@/store/useAuthStore'

const fade = {
  hidden: { opacity: 0, y: 18 },
  show: (delay = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] },
  }),
}

const pains = [
  {
    title: 'The file is never in one place',
    body: 'MCA PDFs, charge searches, MSME delays, a legal dump, and three news tabs. The first read is assembling the packet, not forming a view.',
  },
  {
    title: 'The committee wants a view, not a scrape',
    body: 'Someone still has to write strengths, red flags, and a recommendation. Spreadsheets do not walk into the meeting on their own.',
  },
  {
    title: 'Peers and news arrive too late',
    body: 'Comparables live in last year’s pitch. Headlines sit outside the filing pack. The call gets made on whichever tab was open last.',
  },
]

const steps = [
  {
    n: '01',
    title: 'Name the legal entity',
    body: 'Search MCA companies and LLPs. Pick the CIN you actually mean to underwrite — not a lookalike group company.',
  },
  {
    n: '02',
    title: 'Load the official record',
    body: 'Standalone filings, ratios, charges, MSME supplier delays, and legal history come in from Probe. Charts are drawn from those numbers, not from the model.',
  },
  {
    n: '03',
    title: 'Read, challenge, download',
    body: 'One credit pass writes the first view. Ask follow-ups, add peers or your Excel, and take a committee memo as PDF or Word.',
  },
]

const outcomes = [
  {
    icon: FileText,
    title: 'A memo you can defend',
    body: 'A fresh write-up for the credit committee — not a print of the chat. Filings, peers, and your notes sit in the same packet.',
  },
  {
    icon: BarChart3,
    title: 'Charts from the books',
    body: 'P&L, leverage, cash flow, and peer revenue from Probe. The model does not draw the graphs. The filings do.',
  },
  {
    icon: Search,
    title: 'A chat that already knows the company',
    body: 'Follow up on CCC, a charge, a rating action, or a peer. The workspace keeps the borrower in context.',
  },
]

function ProductStage() {
  return (
    <div className="glass-panel relative overflow-hidden rounded-2xl border shadow-2xl shadow-foreground/5 sm:rounded-3xl">
      <div className="flex items-center justify-between gap-2 border-b border-border/60 px-3 py-3 sm:px-4">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-muted-foreground">
            Sample first read
          </p>
        </div>
        <p className="hidden font-mono text-[10px] text-muted-foreground sm:block">
          CIN L74120MH1985PLC035308
        </p>
      </div>
      <div className="grid lg:grid-cols-[0.92fr_1.08fr]">
        <div className="border-b border-border/60 p-4 sm:p-5 lg:border-b-0 lg:border-r">
          <p className="font-display text-xl leading-tight text-foreground sm:text-2xl">
            Godrej Properties Limited
          </p>
          <p className="mt-1 text-xs text-muted-foreground">Maharashtra · real estate · standalone FY24</p>
          <div className="mt-5 inline-flex items-center rounded-full bg-emerald-700/12 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-emerald-800 dark:bg-emerald-400/15 dark:text-emerald-300">
            Advance with monitoring
          </div>
          <dl className="mt-6 grid grid-cols-3 gap-1.5 sm:gap-3">
            {[
              ['Revenue', '₹3,033 cr'],
              ['EBITDA', '18.2%'],
              ['ICR', '4.6x'],
            ].map(([label, value]) => (
              <div key={label} className="min-w-0 rounded-xl border border-border/70 bg-background/70 px-1.5 py-3 sm:px-3">
                <dt className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</dt>
                <dd className="mt-1 truncate text-sm font-medium tabular-nums sm:text-base">{value}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-5 text-[11px] leading-relaxed text-muted-foreground">
            Illustrative packet. Live reads use the filings of the company you select.
          </p>
        </div>
        <div className="space-y-4 p-4 sm:p-5">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-emerald-800 dark:text-emerald-300">
              Strengths
            </p>
            <ul className="mt-2 space-y-1.5 text-sm leading-relaxed text-foreground/85">
              <li>Godrej brand and group backing; residential bookings scale across Mumbai, NCR, and Bengaluru.</li>
              <li>Liquidity and capital-market access stay visible in the charge and rating record.</li>
            </ul>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-rose-800 dark:text-rose-300">
              Red flags
            </p>
            <ul className="mt-2 space-y-1.5 text-sm leading-relaxed text-foreground/85">
              <li>Collections lag bookings — construction and land spend need a cap against unsold inventory.</li>
              <li>Group land and JV vehicles sit in the related-party pack; keep them in monitoring.</li>
            </ul>
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            {['Committee memo', 'Peer revenue', 'Cited news'].map((chip) => (
              <span
                key={chip}
                className="rounded-full border border-border/70 bg-background/60 px-2.5 py-1 text-[11px] text-muted-foreground"
              >
                {chip}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export function LandingPage() {
  const status = useAuthStore((s) => s.status)
  const signedIn = status === 'authenticated'

  return (
    <div className="relative min-h-dvh">
      <div className="mesh-bg pointer-events-none absolute inset-0" />
      <div className="landing-grid pointer-events-none absolute inset-0" />

      <header className="relative z-20 mx-auto flex w-full max-w-6xl items-center gap-2 px-3 py-3 pt-[max(0.75rem,env(safe-area-inset-top))] sm:px-6 sm:py-4">
        <Link to="/" aria-label="Kuber home" className="relative z-10 shrink-0">
          <KuberLogo size={30} showWordmark />
        </Link>
        <nav className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-6 text-sm text-muted-foreground md:flex">
          <a href="#product" className="hover:text-foreground">
            Product
          </a>
          <a href="#how" className="hover:text-foreground">
            How it works
          </a>
          <a href="#why" className="hover:text-foreground">
            Why Kuber
          </a>
        </nav>
        <div className="relative z-10 ml-auto flex shrink-0 items-center gap-1.5">
          {signedIn ? (
            <Button asChild className="h-8 rounded-full px-3 text-xs sm:h-9 sm:px-4 sm:text-sm">
              <Link to="/app">Open workspace</Link>
            </Button>
          ) : (
            <>
              <Button variant="ghost" asChild className="hidden sm:inline-flex">
                <Link to="/login">Log in</Link>
              </Button>
              <Button asChild className="h-8 rounded-full px-3 text-xs sm:h-9 sm:px-4 sm:text-sm">
                <Link to="/register">Join</Link>
              </Button>
            </>
          )}
          <ThemeToggle className="h-8 w-8" />
        </div>
      </header>

      <nav className="relative z-10 mx-auto flex w-full max-w-6xl gap-4 overflow-x-auto px-3 pb-1 text-xs text-muted-foreground md:hidden">
        <a href="#product" className="shrink-0 py-1 hover:text-foreground">
          Product
        </a>
        <a href="#how" className="shrink-0 py-1 hover:text-foreground">
          How it works
        </a>
        <a href="#why" className="shrink-0 py-1 hover:text-foreground">
          Why Kuber
        </a>
      </nav>

      <main>
        <section className="relative z-10 mx-auto w-full max-w-6xl px-4 pb-10 pt-6 sm:px-6 sm:pt-16">
          <motion.p
            custom={0.02}
            variants={fade}
            initial="hidden"
            animate="show"
            className="max-w-full text-[10px] font-semibold uppercase tracking-[0.14em] text-[#C4A574] sm:text-[11px] sm:tracking-[0.22em]"
          >
            Credit intelligence · Indian corporates
          </motion.p>
          <motion.h1
            custom={0.08}
            variants={fade}
            initial="hidden"
            animate="show"
            className="font-display mt-4 max-w-4xl text-[1.85rem] leading-[1.15] tracking-tight text-pretty text-foreground sm:mt-5 sm:text-5xl sm:leading-[1.08] lg:text-6xl"
          >
            Understand the borrower{' '}
            <em className="italic text-foreground/65">before you take the risk.</em>
          </motion.h1>
          <motion.p
            custom={0.16}
            variants={fade}
            initial="hidden"
            animate="show"
            className="mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg"
          >
            The expensive mistake is not a slow file. It is saying yes while leverage, legal,
            MSME delays, and the news are still sitting in fourteen tabs — and the committee
            asks what you missed.
          </motion.p>
          <motion.div
            custom={0.24}
            variants={fade}
            initial="hidden"
            animate="show"
            className="mt-8 flex w-full max-w-md flex-col gap-3 sm:max-w-none sm:flex-row sm:flex-wrap sm:items-center"
          >
            {signedIn ? (
              <Button size="lg" asChild className="h-11 w-full rounded-full px-6 sm:w-auto">
                <Link to="/app">
                  Continue to workspace
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            ) : (
              <>
                <Button size="lg" asChild className="h-11 w-full rounded-full px-6 sm:w-auto">
                  <Link to="/register">
                    Start a credit read
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild className="h-11 w-full rounded-full px-6 sm:w-auto">
                  <Link to="/login">I already have a desk</Link>
                </Button>
              </>
            )}
          </motion.div>
          <motion.ul
            custom={0.32}
            variants={fade}
            initial="hidden"
            animate="show"
            className="mt-8 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground"
          >
            {['MCA filings', 'Charges & legal', 'MSME delays', 'Peer revenue', 'Cited web search', 'PDF / Word memo'].map(
              (item) => (
                <li key={item} className="flex items-center gap-2">
          <span className="h-1 w-1 rounded-full bg-[#C4A574]" />
                  {item}
                </li>
              )
            )}
          </motion.ul>
        </section>

        <section id="product" className="relative z-10 mx-auto w-full max-w-6xl scroll-mt-24 px-4 pb-16 sm:px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.28, ease: [0.22, 1, 0.36, 1] }}
          >
            <ProductStage />
          </motion.div>
        </section>

        <section id="why" className="relative z-10 mx-auto w-full max-w-6xl scroll-mt-24 px-4 py-8 sm:px-6 sm:py-14">
          <div className="hairline mb-10 h-px w-full" />
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
            The gap
          </p>
          <h2 className="font-display mt-3 max-w-3xl text-[1.65rem] leading-tight sm:text-4xl">
            Credit still lives in fourteen tabs. The decision does not.
          </h2>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {pains.map((pain, index) => (
              <motion.article
                key={pain.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08 }}
                className="rounded-2xl border border-border/70 bg-card/50 p-5"
              >
                <p className="font-mono text-[11px] text-muted-foreground">{String(index + 1).padStart(2, '0')}</p>
                <h3 className="mt-3 text-base font-semibold leading-snug">{pain.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{pain.body}</p>
              </motion.article>
            ))}
          </div>
        </section>

        <section id="how" className="relative z-10 mx-auto w-full max-w-6xl scroll-mt-24 px-4 py-10 sm:px-6 sm:py-16">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
            How a read works
          </p>
          <h2 className="font-display mt-3 max-w-3xl text-[1.65rem] leading-tight sm:text-4xl">
            Name the borrower. Load the books. Leave with a view.
          </h2>
          <div className="mt-10 grid gap-px overflow-hidden rounded-2xl border border-border/70 bg-border/70 md:grid-cols-3">
            {steps.map((step, index) => (
              <motion.article
                key={step.n}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.07 }}
                className="bg-card/80 p-6"
              >
                <p className="font-display text-3xl text-foreground/25">{step.n}</p>
                <h3 className="mt-4 text-base font-semibold">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{step.body}</p>
              </motion.article>
            ))}
          </div>
        </section>

        <section className="relative z-10 mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-12">
          <div className="grid gap-4 md:grid-cols-3">
            {outcomes.map((item, index) => (
              <motion.article
                key={item.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08 }}
                className="glass-panel rounded-2xl p-6"
              >
                <item.icon className="h-5 w-5 text-foreground/70" />
                <h3 className="mt-4 text-base font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
              </motion.article>
            ))}
          </div>
        </section>

        <section className="relative z-10 mx-auto w-full max-w-6xl px-4 py-10 sm:px-6 sm:py-16">
          <div className="grid items-center gap-8 rounded-2xl border border-border/70 bg-card/40 px-4 py-8 sm:rounded-3xl sm:px-12 sm:py-10 lg:grid-cols-[1.1fr_0.9fr]">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
                Built for the desk
              </p>
              <h2 className="font-display mt-3 text-[1.65rem] leading-tight sm:text-4xl">
                Numbers first. Narrative second. News only when it is cited.
              </h2>
              <ul className="mt-6 space-y-3 text-sm leading-relaxed text-muted-foreground">
                <li className="flex gap-3">
                  <Scale className="mt-0.5 h-4 w-4 shrink-0 text-foreground/60" />
                  Assessments stay tied to standalone filings. The model does not invent a P&amp;L.
                </li>
                <li className="flex gap-3">
                  <Newspaper className="mt-0.5 h-4 w-4 shrink-0 text-foreground/60" />
                  Web search is for ratings, litigation, and what the statements omit — with a paper trail.
                </li>
                <li className="flex gap-3">
                  <Gavel className="mt-0.5 h-4 w-4 shrink-0 text-foreground/60" />
                  Legal history and MSME delays sit in the same read as leverage and liquidity.
                </li>
                <li className="flex gap-3">
                  <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-foreground/60" />
                  Your keys and filings stay on your API. The browser is the desk, not the vault.
                </li>
              </ul>
            </div>
            <div className="rounded-2xl border border-[#C4A574]/35 bg-background/70 p-6">
              <p className="font-display text-xl leading-snug">
                “Named for Kubera — the treasurer. A workspace that keeps the books in view.”
              </p>
              <p className="mt-4 text-sm text-muted-foreground">
                Search the entity, wait for the first pass, then interrogate it. Add peers from the
                chart. Attach your CMA. Take the memo into the room.
              </p>
            </div>
          </div>
        </section>

        <section className="relative z-10 mx-auto w-full max-w-6xl px-4 pb-20 sm:px-6">
          <div className="overflow-hidden rounded-2xl bg-[#161D28] px-4 py-10 text-[#F4EFE6] sm:rounded-3xl sm:px-12 sm:py-12">
            <h2 className="font-display text-[1.75rem] leading-tight sm:text-5xl sm:leading-[1.12]">
              Run the next name through Kuber.
            </h2>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-[#F4EFE6]/70 sm:text-base">
              Create an account, pick a CIN, and ask for a credit view. Follow-ups stay on that
              borrower. The memo is a document, not a screenshot of the chat.
            </p>
            <div className="mt-8 flex w-full max-w-md flex-col gap-3 sm:max-w-none sm:flex-row sm:flex-wrap">
              {signedIn ? (
                <Button
                  size="lg"
                  asChild
                  className="h-11 w-full rounded-full bg-[#F4EFE6] px-6 text-[#161D28] hover:bg-[#F4EFE6]/90 sm:w-auto"
                >
                  <Link to="/app">Open workspace</Link>
                </Button>
              ) : (
                <>
                  <Button
                    size="lg"
                    asChild
                    className="h-11 w-full rounded-full bg-[#F4EFE6] px-6 text-[#161D28] hover:bg-[#F4EFE6]/90 sm:w-auto"
                  >
                    <Link to="/register">Create an account</Link>
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    asChild
                    className="h-11 w-full rounded-full border-[#F4EFE6]/25 bg-transparent px-6 text-[#F4EFE6] hover:bg-[#F4EFE6]/10 hover:text-[#F4EFE6] sm:w-auto"
                  >
                    <Link to="/login">Log in</Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        </section>
      </main>

      <footer className="relative z-10 border-t border-border/40 px-4 py-8 pb-[max(2rem,env(safe-area-inset-bottom))] text-center text-xs text-muted-foreground sm:px-6">
        Kuber · Indian corporate credit reads from filings, legal, MSME, and cited web search
      </footer>
    </div>
  )
}
