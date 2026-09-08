import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ArrowRight, FileSearch, Newspaper, ShieldCheck, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { KuberLogo } from '@/components/KuberLogo'
import { ThemeToggle } from '@/components/ThemeToggle'
import { useAuthStore } from '@/store/useAuthStore'

const features = [
  {
    icon: FileSearch,
    title: 'MCA filings, in one place',
    body: 'Search any Indian company and pull standalone statements, ratios, charges, and compliance flags from official filings.',
  },
  {
    icon: Newspaper,
    title: 'News with the numbers',
    body: 'Live web search sits next to the books, so ratings actions, litigation, and headlines are cited instead of guessed.',
  },
  {
    icon: ShieldCheck,
    title: 'A credit view you can defend',
    body: 'One assessment covering P&L, leverage, MSME delays, legal exposure, and a clear risk conclusion.',
  },
]

const fadeUp = {
  hidden: { opacity: 0, y: 18 },
  show: (delay) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] },
  }),
}

export function LandingPage() {
  const status = useAuthStore((s) => s.status)
  const signedIn = status === 'authenticated'

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mesh-bg pointer-events-none absolute inset-0" />
      <motion.div
        aria-hidden
        className="pointer-events-none absolute -left-24 top-24 h-72 w-72 rounded-full bg-primary/20 blur-3xl"
        animate={{ y: [0, -16, 0], opacity: [0.45, 0.7, 0.45] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        aria-hidden
        className="pointer-events-none absolute -right-16 bottom-10 h-80 w-80 rounded-full bg-emerald-400/15 blur-3xl"
        animate={{ y: [0, 18, 0], opacity: [0.35, 0.6, 0.35] }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
      />

      <header className="relative z-10 mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-5">
        <KuberLogo size={36} showWordmark />
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

      <main className="relative z-10 mx-auto grid w-full max-w-6xl gap-12 px-6 pb-20 pt-8 lg:grid-cols-[1.1fr_0.9fr] lg:pt-16">
        <div>
          <motion.p
            custom={0.05}
            variants={fadeUp}
            initial="hidden"
            animate="show"
            className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-card/70 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur"
          >
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            Credit intelligence for Indian corporates
          </motion.p>
          <motion.h1
            custom={0.12}
            variants={fadeUp}
            initial="hidden"
            animate="show"
            className="mt-5 text-4xl font-semibold tracking-tight text-foreground sm:text-5xl"
          >
            Read a company the way a credit analyst would.
          </motion.h1>
          <motion.p
            custom={0.2}
            variants={fadeUp}
            initial="hidden"
            animate="show"
            className="mt-4 max-w-xl text-base leading-relaxed text-muted-foreground"
          >
            Kuber turns MCA filings, legal history, and current news into a single credit
            assessment. Search by name, pick a CIN, and get tables, red flags, and a
            risk conclusion in one pass.
          </motion.p>
          <motion.div
            custom={0.28}
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
                  <Link to="/register">Create an account</Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link to="/login">Log in</Link>
                </Button>
              </>
            )}
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
          className="glass-panel relative rounded-3xl border p-6 shadow-xl"
        >
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Sample workspace
          </p>
          <p className="mt-2 text-lg font-semibold">Godrej Properties Limited</p>
          <p className="text-sm text-muted-foreground">CIN L74120MH1985PLC035308</p>
          <div className="mt-5 grid grid-cols-3 gap-3 text-center">
            {[
              ['Revenue', 'Filed'],
              ['Leverage', 'Tracked'],
              ['News', 'Cited'],
            ].map(([label, value], index) => (
              <motion.div
                key={label}
                className="rounded-xl border border-border/60 bg-background/50 px-2 py-3"
                animate={{ y: [0, index % 2 === 0 ? -6 : 6, 0] }}
                transition={{ duration: 4 + index, repeat: Infinity, ease: 'easeInOut' }}
              >
                <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
                <p className="mt-1 text-sm font-medium">{value}</p>
              </motion.div>
            ))}
          </div>
          <div className="mt-5 space-y-2 text-sm text-muted-foreground">
            <p>1. Load filings from Probe</p>
            <p>2. Write tables, legal, and MSME in one model pass</p>
            <p>3. Pull live web search for what the statements omit</p>
          </div>
        </motion.div>
      </main>

      <section className="relative z-10 mx-auto grid w-full max-w-6xl gap-4 px-6 pb-24 sm:grid-cols-3">
        {features.map((feature, index) => (
          <motion.article
            key={feature.title}
            custom={0.35 + index * 0.08}
            variants={fadeUp}
            initial="hidden"
            animate="show"
            whileHover={{ y: -6 }}
            className="glass-panel rounded-2xl border p-5"
          >
            <feature.icon className="h-5 w-5 text-primary" />
            <h2 className="mt-3 text-sm font-semibold">{feature.title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{feature.body}</p>
          </motion.article>
        ))}
      </section>
    </div>
  )
}
