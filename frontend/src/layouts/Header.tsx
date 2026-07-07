/**
 * Header — top application bar.
 *
 * Displays the current page breadcrumb derived from the route and
 * a placeholder user area (avatar + name) for future auth integration.
 *
 * No API calls. No state. Pure presentational.
 */

import { useMatches } from 'react-router-dom'

// ---------------------------------------------------------------------------
// Breadcrumb — driven by route handle metadata
// ---------------------------------------------------------------------------

interface RouteHandle {
  breadcrumb?: string
}

function Breadcrumb() {
  const matches = useMatches()

  const crumbs = matches
    .filter((m) => Boolean((m.handle as RouteHandle | undefined)?.breadcrumb))
    .map((m) => (m.handle as RouteHandle).breadcrumb as string)

  if (crumbs.length === 0) return null

  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex items-center gap-2 text-sm text-slate-400">
        {crumbs.map((crumb, i) => (
          <li key={crumb} className="flex items-center gap-2">
            {i > 0 && (
              <span aria-hidden="true" className="text-slate-600">
                /
              </span>
            )}
            <span
              className={
                i === crumbs.length - 1 ? 'font-medium text-white' : ''
              }
            >
              {crumb}
            </span>
          </li>
        ))}
      </ol>
    </nav>
  )
}

// ---------------------------------------------------------------------------
// User avatar placeholder
// ---------------------------------------------------------------------------

function UserAvatar() {
  return (
    <div className="flex items-center gap-3">
      {/* Notification bell — placeholder */}
      <button
        type="button"
        className="relative flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-white/5 hover:text-slate-200"
        aria-label="Notifications"
        id="header-notifications-btn"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.75}
          strokeLinecap="round"
          strokeLinejoin="round"
          className="h-[18px] w-[18px]"
          aria-hidden="true"
        >
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
      </button>

      {/* Divider */}
      <div className="h-6 w-px bg-white/10" aria-hidden="true" />

      {/* User pill */}
      <button
        type="button"
        className="flex items-center gap-2.5 rounded-lg px-2 py-1.5 transition-colors hover:bg-white/5"
        aria-label="User menu"
        id="header-user-menu-btn"
      >
        {/* Avatar initials */}
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-[11px] font-bold text-white">
          EA
        </div>
        <span className="text-sm font-medium text-slate-200">Enterprise Admin</span>
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          className="h-3.5 w-3.5 text-slate-500"
          aria-hidden="true"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

export function Header() {
  return (
    <header
      id="app-header"
      className="flex h-14 flex-shrink-0 items-center justify-between border-b border-white/8 bg-slate-950/80 px-6 backdrop-blur-sm"
    >
      <Breadcrumb />
      <UserAvatar />
    </header>
  )
}
