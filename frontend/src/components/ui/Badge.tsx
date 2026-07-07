/**
 * Badge — inline status indicator pill.
 *
 * Variants:
 *   healthy   → emerald
 *   degraded  → amber
 *   unhealthy → red
 *   info      → blue
 *   neutral   → slate
 */

import { cn } from '@/utils/cn'

type BadgeVariant = 'healthy' | 'degraded' | 'unhealthy' | 'info' | 'neutral'

interface BadgeProps {
  /** Visual treatment. */
  variant?: BadgeVariant
  /** Badge label text. */
  children: React.ReactNode
  /** Additional Tailwind classes. */
  className?: string
  /** Render a pulsing status dot before the text. */
  withDot?: boolean
}

const variantStyles: Record<BadgeVariant, string> = {
  healthy:
    'bg-emerald-500/15 text-emerald-400 ring-1 ring-inset ring-emerald-500/25',
  degraded:
    'bg-amber-500/15 text-amber-400 ring-1 ring-inset ring-amber-500/25',
  unhealthy:
    'bg-red-500/15 text-red-400 ring-1 ring-inset ring-red-500/25',
  info:
    'bg-blue-500/15 text-blue-400 ring-1 ring-inset ring-blue-500/25',
  neutral:
    'bg-slate-500/15 text-slate-400 ring-1 ring-inset ring-slate-500/25',
}

const dotStyles: Record<BadgeVariant, string> = {
  healthy: 'bg-emerald-400',
  degraded: 'bg-amber-400',
  unhealthy: 'bg-red-400',
  info: 'bg-blue-400',
  neutral: 'bg-slate-400',
}

export function Badge({
  variant = 'neutral',
  children,
  className,
  withDot = false,
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium',
        variantStyles[variant],
        className,
      )}
    >
      {withDot && (
        <span
          className={cn(
            'h-1.5 w-1.5 rounded-full',
            dotStyles[variant],
            variant === 'healthy' && 'animate-pulse',
          )}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  )
}
