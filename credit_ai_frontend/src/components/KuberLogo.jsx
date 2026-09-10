import { cn } from '@/lib/utils'

export function KuberMark({ size = 32, className }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <rect width="48" height="48" rx="12" fill="#161D28" />
      <rect x="13.2" y="11" width="6.6" height="26" rx="1.15" fill="#F4EFE6" />
      <path d="M22.3 11h14.2L27.8 23.3H22.3V11Z" fill="#F4EFE6" />
      <path d="M22.3 25.5h6.2L37.4 37H31.4L22.3 25.5Z" fill="#F4EFE6" />
      <circle cx="34.1" cy="21.4" r="4.55" fill="#C4A574" />
      <circle cx="34.1" cy="21.4" r="3.15" fill="none" stroke="#EAD7A8" strokeWidth="0.55" />
      <circle cx="34.1" cy="21.4" r="1.15" fill="#161D28" fillOpacity="0.28" />
    </svg>
  )
}

export function KuberLogo({ className, size = 32, showWordmark = false }) {
  return (
    <div className={cn('flex items-center gap-2.5', className)}>
      <KuberMark size={size} />
      {showWordmark && (
        <span className="kuber-wordmark font-display truncate text-[1.2rem] leading-none tracking-tight text-foreground sm:text-[1.35rem]">
          Kuber
        </span>
      )}
    </div>
  )
}
