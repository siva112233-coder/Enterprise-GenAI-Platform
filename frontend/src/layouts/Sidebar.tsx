/**
 * Sidebar — fixed left navigation panel.
 *
 * Renders the logo, primary nav items, and footer nav items.
 * Active state is derived from React Router's `useLocation` —
 * no external state management needed.
 */

import { NavLink, useLocation } from 'react-router-dom'
import { cn } from '@/utils/cn'
import { FOOTER_NAV_ITEMS, PRIMARY_NAV_ITEMS } from '@/utils/constants'
import type { NavItem } from '@/types'

// ---------------------------------------------------------------------------
// Logo mark
// ---------------------------------------------------------------------------

function LogoMark() {
  return (
    <div className="flex items-center gap-3 px-4 py-5 border-b border-white/8">
      {/* Geometric logo — no image dep */}
      <div className="relative h-8 w-8 flex-shrink-0">
        <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/30" />
        <div className="absolute inset-0 flex items-center justify-center">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            className="h-4 w-4 text-white"
            aria-hidden="true"
          >
            <path
              d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </div>
      <div className="flex flex-col min-w-0">
        <span className="text-sm font-semibold text-white leading-tight truncate">
          Enterprise GenAI
        </span>
        <span className="text-[10px] font-medium text-slate-400 tracking-widest uppercase">
          Platform
        </span>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Nav item
// ---------------------------------------------------------------------------

function SidebarNavItem({ item }: { item: NavItem }) {
  const location = useLocation()
  const isActive =
    item.path === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(item.path)

  const Icon = item.icon

  return (
    <NavLink
      to={item.path}
      className={cn(
        'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150',
        isActive
          ? 'bg-white/10 text-white shadow-sm'
          : 'text-slate-400 hover:bg-white/5 hover:text-slate-200',
      )}
      aria-current={isActive ? 'page' : undefined}
    >
      {/* Active indicator bar */}
      {isActive && (
        <span
          className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-violet-400"
          aria-hidden="true"
        />
      )}

      <Icon
        className={cn(
          'h-[18px] w-[18px] flex-shrink-0 transition-colors',
          isActive ? 'text-violet-400' : 'text-slate-500 group-hover:text-slate-300',
        )}
      />

      <span className="truncate">{item.label}</span>

      {item.badge != null && item.badge > 0 && (
        <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-violet-500/20 px-1.5 text-[10px] font-semibold text-violet-300">
          {item.badge > 99 ? '99+' : item.badge}
        </span>
      )}
    </NavLink>
  )
}

// ---------------------------------------------------------------------------
// Sidebar
// ---------------------------------------------------------------------------

export function Sidebar() {
  return (
    <aside
      id="sidebar"
      className="flex h-full w-60 flex-shrink-0 flex-col bg-slate-900 border-r border-white/8"
      aria-label="Main navigation"
    >
      <LogoMark />

      {/* Primary navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
          Navigation
        </p>
        {PRIMARY_NAV_ITEMS.map((item) => (
          <SidebarNavItem key={item.id} item={item} />
        ))}
      </nav>

      {/* Footer navigation */}
      <div className="border-t border-white/8 px-3 py-3 space-y-0.5">
        {FOOTER_NAV_ITEMS.map((item) => (
          <SidebarNavItem key={item.id} item={item} />
        ))}
      </div>
    </aside>
  )
}
