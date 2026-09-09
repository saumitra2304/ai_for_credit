import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Building2,
  FileSearch,
  Gavel,
  Globe2,
  LineChart,
  Newspaper,
  Scale,
  ShieldCheck,
  Sparkles,
  Target,
  Workflow,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { KuberLogo } from '@/components/KuberLogo'
import { ThemeToggle } from '@/components/ThemeToggle'
import { useAuthStore } from '@/store/useAuthStore'

const fadeUp = {
  hidden: { opacity: 0, y: 22 },
  show: (delay = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, delay, ease: [0.22, 1, 0.36, 1] },
  }),
}

const steps = [
  {
    n: '01',
    title: 'Find the company',
    body: 'Search MCA names and CINs. Select the legal entity you actually mean to underwrite.',
  },
  {
    n: '02',
    title: 'Load the books',
    body: 'Pull standalone filings, ratios, charges, MSME delays, and legal history from official sources.',
  },
  {
    n: '03',
    title: 'One credit pass',
    body: 'GPT-5.4 nano writes tables, red flags, and a risk conclusion, with live web search for news the filings omit.',
  },
]

const goals = [
  {
    icon: Target,
    title: 'Faster first reads',
    body: 'Cut the time from “who is this borrower?” to a structured credit view you can discuss.',
  },
  {
    icon: Scale,
    title: 'Numbers before narrative',
    body: 'Assessments stay tied to filings. Headlines are cited from web search, not invented.',
  },
  {
    icon: ShieldCheck,
    title: 'Defensible conclusions',
    body: 'Leverage, liquidity, legal exposure, and MSME behaviour sit in one place so a credit call has a paper trail.',
  },
]

const features = [
  {
    icon: FileSearch,
    title: 'MCA filings, assembled',
    body: 'Standalone statements, ratios, charges, and compliance flags for Indian companies and LLPs.',
  },
  {
    icon: Newspaper,
    title: 'News next to the books',
    body: 'OpenAI web search runs in the same model pass for ratings, litigation, and current events.',
  },
  {
    icon: Gavel,
    title: 'Legal and MSME context',
    body: 'Payment delays and legal history are flattened into the assessment, not left in a side PDF.',
  },
  {
    icon: LineChart,
    title: 'Follow-up in the same chat',
    body: 'Ask about a ratio, a year, or a headline. The model answers against the companies already loaded.',
  },
  {
    icon: Globe2,
    title: 'Built for a web team',
    body: 'Sign in from the browser. Keys and filings stay on your API. The workspace is Vercel-hosted.',
  },
  {
    icon: Workflow,
    title: 'One model, one pass',
    body: 'No stitched multi-LLM loop. Filings plus web search go into a single credit write-up.',
  },
]

export function LandingPage() {
  const status = useAuthStore((s) => s.status)
  const signedIn = status === 'authenticated'

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mesh-bg pointer-events-none absolute inset-0" />
      <motion.div
        aria-hidden
        className="pointer-events-none absolute -left-24 top-16 h-80 w-80 rounded-full bg-primary/20 blur-3xl"
        animate={{ y: [0, -20, 0], scale: [1, 1.06, 1] }}
        transition={{ duration: 9, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        aria-hidden
        className="pointer-events-none absolute -right-20 top-40 h-96 w-96 rounded-full bg-emerald-400/15 blur-3xl"
        animate={{ y: [0, 24, 0], opacity: [0.35, 0.65, 0.35] }}
        transition={{ duration: 11, repeat: Infinity, ease: 'easeInOut' }}
      />

      <header className="relative z-10 mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4 sm:px-6 sm:py-5">
        <Link to="/" aria-label="Kuber home">
          <KuberLogo size={36} showWordmark />
        </Link>
        <div className="flex items-center gap-2">
          <ThemeToggle className="h-8 w-8" />
          {signedIn ? (
            <Button asChild>
              <Link to="/app">
                Open workspace
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          ) : (
            <>
              <Button variant="ghost" asChild>
                <Link to="/login">Log in</Link>
              </Button>
              <Button asChild>
                <Link to="/register">Sign up</Link>
              </Button>
            </>
          )}
        </div>
      </header>

      <main className="relative z-10 mx-auto w-full max-w-6xl px-4 pb-8 pt-6 sm:px-6 lg:pt-14">
        <div className="grid gap-12 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div>
            <motion.p
              custom={0.04}
              variants={fadeUp}
              initial="hidden"
              animate="show"
              className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-card/70 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur"
            >
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              Credit intelligence for Indian corporates
            </motion.p>
            <motion.h1
              custom={0.1}
              variants={fadeUp}
              initial="hidden"
              animate="show"
              className="mt-5 text-3xl font-semibold tracking-tight text-foreground sm:text-5xl lg:text-[3.15rem] lg:leading-[1.12]"
            >
              See the borrower before you take the risk.
            </motion.h1>
            <motion.p
              custom={0.18}
              variants={fadeUp}
              initial="hidden"
              animate="show"
              className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground"
            >
              Kuber is a credit workspace: search an Indian company, load MCA filings, and get
              one analyst-style assessment — P&amp;L, leverage, legal, MSME delays, and current
              news — in a single GPT pass with web search.
            </motion.p>
            <motion.div
              custom={0.26}
              variants={fadeUp}
              initial="hidden"
              animate="show"
              className="mt-8 flex flex-wrap gap-3"
            >
              {signedIn ? (
                <Button size="lg" asChild>
                  <Link to="/app">
                    Continue to workspace
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
              ) : (
                <>
                  <Button size="lg" asChild>
                    <Link to="/register">
                      Start a credit read
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button size="lg" variant="outline" asChild>
                    <Link to="/login">Log in</Link>
                  </Button>
                </>
              )}
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, x: 28, rotate: 1.5 }}
            animate={{ opacity: 1, x: 0, rotate: 0 }}
            transition={{ duration: 0.75, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
            className="glass-panel relative overflow-hidden rounded-3xl border p-6 shadow-xl"
          >
            <motion.div
              aria-hidden
              className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/70 to-transparent"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 3.2, repeat: Infinity }}
            />
            <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              <Building2 className="h-3.5 w-3.5" />
              Live workspace preview
            </div>
            <p className="mt-3 text-lg font-semibold">Godrej Properties Limited</p>
            <p className="font-mono text-xs text-muted-foreground">CIN L74120MH1985PLC035308</p>
            <div className="mt-5 grid grid-cols-3 gap-2 text-center sm:gap-3">
              {[
                ['Revenue', 'From filings'],
                ['Leverage', 'Tracked'],
                ['News', 'Web cited'],
              ].map(([label, value], index) => (
                <motion.div
                  key={label}
                  className="rounded-xl border border-border/60 bg-background/50 px-2 py-3"
                  animate={{ y: [0, index % 2 === 0 ? -7 : 7, 0] }}
                  transition={{ duration: 4.2 + index, repeat: Infinity, ease: 'easeInOut' }}
                >
                  <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
                  <p className="mt-1 text-sm font-medium">{value}</p>
                </motion.div>
              ))}
            </div>
            <div className="mt-5 space-y-2.5 text-sm text-muted-foreground">
              {[
                'Probe filings and legal history',
                'One GPT-5.4 nano credit pass',
                'OpenAI web search for what statements omit',
              ].map((line, i) => (
                <motion.p
                  key={line}
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.45 + i * 0.12 }}
                >
                  <span className="mr-2 font-mono text-[11px] text-primary">{String(i + 1).padStart(2, '0')}</span>
                  {line}
                </motion.p>
              ))}
            </div>
          </motion.div>
        </div>
      </main>

      <section className="relative z-10 mx-auto w-full max-w-6xl px-4 py-12 sm:px-6 sm:py-16">
        <motion.h2
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-2xl font-semibold tracking-tight"
        >
          How a read works
        </motion.h2>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          From name search to a credit memo you can interrogate — without hopping across MCA
          PDFs, news tabs, and a blank chat window.
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {steps.map((step, index) => (
            <motion.article
              key={step.n}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-40px' }}
              transition={{ delay: index * 0.08, duration: 0.45 }}
              whileHover={{ y: -6 }}
              className="glass-panel rounded-2xl border p-5"
            >
              <p className="font-mono text-xs text-primary">{step.n}</p>
              <h3 className="mt-3 text-base font-semibold">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{step.body}</p>
            </motion.article>
          ))}
        </div>
      </section>

      <section className="relative z-10 mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">
        <motion.h2
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-2xl font-semibold tracking-tight"
        >
          What we are aiming for
        </motion.h2>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {goals.map((goal, index) => (
            <motion.article
              key={goal.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08 }}
              className="rounded-2xl border border-border/70 bg-card/40 p-5"
            >
              <goal.icon className="h-5 w-5 text-emerald-500" />
              <h3 className="mt-3 text-sm font-semibold">{goal.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{goal.body}</p>
            </motion.article>
          ))}
        </div>
      </section>

      <section className="relative z-10 mx-auto w-full max-w-6xl px-4 py-12 sm:px-6 sm:py-16">
        <motion.h2
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-2xl font-semibold tracking-tight"
        >
          Inside the product
        </motion.h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <motion.article
              key={feature.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ y: -5 }}
              className="glass-panel rounded-2xl border p-5"
            >
              <feature.icon className="h-5 w-5 text-primary" />
              <h3 className="mt-3 text-sm font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{feature.body}</p>
            </motion.article>
          ))}
        </div>
      </section>

      <section className="relative z-10 mx-auto w-full max-w-6xl px-4 pb-20 sm:px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="glass-panel overflow-hidden rounded-3xl border px-5 py-10 text-center sm:px-12"
        >
          <Sparkles className="mx-auto h-6 w-6 text-primary" />
          <h2 className="mt-3 text-2xl font-semibold tracking-tight">
            Run the next name through Kuber
          </h2>
          <p className="mx-auto mt-2 max-w-lg text-sm text-muted-foreground">
            Create an account, pick a CIN, and ask for a credit view. Follow-ups stay in the same
            thread against the companies you already loaded.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            {signedIn ? (
              <Button size="lg" asChild>
                <Link to="/app">Open workspace</Link>
              </Button>
            ) : (
              <>
                <Button size="lg" asChild>
                  <Link to="/register">Create an account</Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link to="/login">Log in</Link>
                </Button>
              </>
            )}
          </div>
        </motion.div>
      </section>

      <footer className="relative z-10 border-t border-border/40 px-6 py-6 text-center text-xs text-muted-foreground">
        Kuber Credit AI · Indian corporate credit reads from filings and cited web search
      </footer>
    </div>
  )
}
