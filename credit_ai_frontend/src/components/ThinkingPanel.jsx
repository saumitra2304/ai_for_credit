import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Check } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { THINKING_STAGES, SCAN_TOKENS, companyLabel, thoughtsForStage } from '@/lib/thinkingSteps'

function stageIndex(stageId) {
  const idx = THINKING_STAGES.findIndex((item) => item.id === stageId)
  return idx < 0 ? 0 : idx
}

function useTypedLine(text) {
  const [typed, setTyped] = useState('')

  useEffect(() => {
    setTyped('')
    if (!text) return undefined
    let i = 0
    const timer = setInterval(() => {
      i += 1
      setTyped(text.slice(0, i))
      if (i >= text.length) clearInterval(timer)
    }, 16)
    return () => clearInterval(timer)
  }, [text])

  return typed
}

export function ThinkingPanel({ companyNames, currentStage, progress }) {
  const stageId = currentStage?.id ?? 'fetch'
  const activeIndex = stageIndex(stageId)
  const name = companyLabel(companyNames)
  const [visibleCount, setVisibleCount] = useState(1)
  const [shownProgress, setShownProgress] = useState(progress ?? 0)
  const [tokenIndex, setTokenIndex] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setShownProgress((prev) => {
        const floor = Math.max(progress ?? 0, 4)
        const creepCap = Math.min(Math.max(floor + 10, floor), 90)
        const target = prev < floor ? floor : Math.min(prev + 0.12, creepCap)
        return Math.abs(target - prev) < 0.08 ? target : prev + (target - prev) * 0.2
      })
    }, 40)
    return () => clearInterval(timer)
  }, [progress])

  const pool = useMemo(() => thoughtsForStage(stageId, companyNames), [stageId, companyNames])

  useEffect(() => {
    setVisibleCount(1)
    const timer = setInterval(() => {
      setVisibleCount((count) => Math.min(count + 1, pool.length))
    }, 1400)
    return () => clearInterval(timer)
  }, [pool])

  useEffect(() => {
    const timer = setInterval(() => {
      setTokenIndex((index) => (index + 1) % SCAN_TOKENS.length)
    }, 900)
    return () => clearInterval(timer)
  }, [])

  const shown = pool.slice(0, visibleCount)
  const liveThought = shown[shown.length - 1] ?? pool[0]
  const typed = useTypedLine(liveThought)
  const prior = shown.slice(0, -1)

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="overflow-hidden rounded-2xl border border-primary/20 bg-card/75 shadow-xl shadow-primary/10 backdrop-blur-md"
    >
      <div className="relative overflow-hidden px-5 pb-4 pt-5">
        <div className="pointer-events-none absolute -right-12 -top-16 h-44 w-44 rounded-full bg-primary/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-16 left-10 h-32 w-32 rounded-full bg-emerald-400/15 blur-3xl" />
        <div className="thinking-scan pointer-events-none absolute inset-x-0 top-0 h-px" />

        <div className="relative flex items-start gap-4">
          <div className="relative mt-0.5 flex h-12 w-12 shrink-0 items-center justify-center">
            <motion.span
              className="absolute inset-0 rounded-full border border-primary/40"
              animate={{ scale: [1, 1.35, 1], opacity: [0.8, 0.1, 0.8] }}
              transition={{ duration: 2.1, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.span
              className="absolute inset-0 rounded-full border border-dashed border-emerald-400/40"
              animate={{ rotate: 360 }}
              transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
            />
            <div className="relative flex h-9 w-9 items-center justify-center rounded-full bg-primary/15">
              <Brain className="h-5 w-5 text-primary" />
            </div>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-primary/85">
              Model thinking
            </p>
            <h3 className="mt-1 text-[15px] font-semibold leading-snug">
              Working through {name}
            </h3>
            <p className="mt-1 text-xs text-muted-foreground">
              {currentStage?.label ?? 'Loading company data'}
            </p>
          </div>
          <span className="font-mono text-[11px] tabular-nums text-muted-foreground">
            {Math.round(shownProgress)}%
          </span>
        </div>

        <div className="relative mt-4 flex flex-wrap gap-1.5">
          {THINKING_STAGES.map((stage, index) => {
            const done = index < activeIndex
            const active = index === activeIndex
            return (
              <motion.div
                key={stage.id}
                layout
                className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-medium ${
                  active
                    ? 'bg-primary/15 text-primary ring-1 ring-primary/25'
                    : done
                      ? 'bg-emerald-500/10 text-emerald-500'
                      : 'bg-muted/60 text-muted-foreground'
                }`}
              >
                {done ? (
                  <Check className="h-3 w-3" />
                ) : active ? (
                  <motion.span
                    className="h-1.5 w-1.5 rounded-full bg-primary"
                    animate={{ opacity: [1, 0.2, 1] }}
                    transition={{ duration: 0.9, repeat: Infinity }}
                  />
                ) : (
                  <span className="h-1.5 w-1.5 rounded-full bg-border" />
                )}
                {stage.label}
              </motion.div>
            )
          })}
        </div>

        <div className="relative mt-4">
          <Progress value={shownProgress} className="h-1.5 overflow-hidden" />
          <div className="thinking-scan pointer-events-none absolute inset-0 rounded-full opacity-70" />
        </div>

        <div className="relative mt-3 flex flex-wrap gap-1.5">
          {SCAN_TOKENS.map((token, index) => {
            const active = index === tokenIndex
            const near = Math.abs(index - tokenIndex) === 1
            return (
              <span
                key={token}
                className={`rounded-md px-2 py-0.5 font-mono text-[10px] transition-all duration-300 ${
                  active
                    ? 'bg-primary/20 text-primary'
                    : near
                      ? 'bg-muted/80 text-foreground/70'
                      : 'bg-muted/40 text-muted-foreground/70'
                }`}
              >
                {token}
              </span>
            )
          })}
        </div>
      </div>

      <div className="border-t border-border/50 bg-background/45 px-5 py-4">
        <p className="mb-3 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
          Live reasoning
        </p>
        <div className="space-y-2">
          <AnimatePresence initial={false}>
            {prior.map((thought) => (
              <motion.p
                key={`${stageId}-${thought}`}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 0.45, x: 0 }}
                className="text-sm leading-relaxed text-muted-foreground"
              >
                {thought}
              </motion.p>
            ))}
          </AnimatePresence>
          <p className="min-h-[1.4em] text-sm leading-relaxed text-foreground">
            <motion.span
              className="mr-2 inline-block h-1.5 w-1.5 rounded-full bg-primary align-middle"
              animate={{ opacity: [1, 0.2, 1] }}
              transition={{ duration: 0.85, repeat: Infinity }}
            />
            {typed}
            <motion.span
              className="ml-0.5 inline-block h-4 w-px bg-primary align-middle"
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 0.7, repeat: Infinity }}
            />
          </p>
        </div>

        <div className="mt-4 space-y-2">
          {[92, 74, 81, 58].map((width, index) => (
            <motion.div
              key={width}
              className="h-2 rounded-full bg-muted/70"
              style={{ width: `${width}%` }}
              animate={{ opacity: [0.25, 0.55, 0.25] }}
              transition={{ duration: 1.6, delay: index * 0.18, repeat: Infinity }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}
