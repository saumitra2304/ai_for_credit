import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { applyTheme, getTheme } from '@/lib/theme'

export function ThemeToggle({ className }) {
  const [theme, setTheme] = useState(() => getTheme())

  useEffect(() => {
    applyTheme(theme)
  }, [theme])

  const next = theme === 'dark' ? 'light' : 'dark'

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className={className ?? 'h-7 w-7'}
          onClick={() => setTheme(next)}
          aria-label={`Switch to ${next} mode`}
        >
          {theme === 'dark' ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
        </Button>
      </TooltipTrigger>
      <TooltipContent>{next === 'light' ? 'Light mode' : 'Dark mode'}</TooltipContent>
    </Tooltip>
  )
}
