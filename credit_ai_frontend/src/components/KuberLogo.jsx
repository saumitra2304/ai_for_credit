import { cn } from '@/lib/utils'

export function KuberLogo({ className, size = 32, showWordmark = false }) {
  return (
    <div className={cn('flex items-center gap-2.5', className)}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <rect width="48" height="48" rx="12" fill="url(#kuber-bg)" />
        <path
          d="M15 33V15h4.5l8.2 11.8V15H32v18h-4.4L19.4 21.2V33H15z"
          fill="white"
        />
        <path
          d="M28 33V23l6-8h5l-7.5 10.2V33H28z"
          fill="#A7F3D0"
        />
        <circle cx="36" cy="14" r="3.5" fill="#34D399" />
        <defs>
          <linearGradient id="kuber-bg" x1="4" y1="4" x2="44" y2="44">
            <stop stopColor="#2563EB" />
            <stop offset="1" stopColor="#059669" />
          </linearGradient>
        </defs>
      </svg>
      {showWordmark && (
        <span className="text-base font-semibold tracking-tight text-foreground">
          Kuber
        </span>
      )}
    </div>
  )
}
