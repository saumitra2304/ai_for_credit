import { motion } from 'framer-motion'
import { Progress } from '@/components/ui/progress'
import { Loader2 } from 'lucide-react'

export function AnalysisProgress({ progress, currentStage }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="mx-4 my-3 rounded-xl border border-border/40 bg-card/40 px-4 py-3 backdrop-blur-sm"
    >
      <div className="mb-2.5 flex items-center gap-2.5">
        <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
        <p className="flex-1 text-xs font-medium text-foreground">
          {currentStage?.label ?? 'Initializing...'}
        </p>
        <span className="text-[10px] font-mono text-muted-foreground">{progress}%</span>
      </div>
      <Progress value={progress} className="h-1" />
    </motion.div>
  )
}
