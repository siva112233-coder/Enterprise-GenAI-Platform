/**
 * NotFound — 404 fallback page.
 *
 * Rendered by the router's `errorElement` / catch-all route.
 */

import { Link } from 'react-router-dom'
import { usePageTitle } from '@/hooks/usePageTitle'
import { ROUTES } from '@/utils/constants'

export default function NotFoundPage() {
  usePageTitle('404 — Page Not Found')

  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-6 px-8 py-20 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-white/8 bg-slate-900">
        <span className="text-4xl font-bold text-slate-600" aria-hidden="true">
          ?
        </span>
      </div>

      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold text-white">Page not found</h1>
        <p className="text-sm text-slate-400">
          The page you are looking for does not exist or has been moved.
        </p>
      </div>

      <Link
        to={ROUTES.DASHBOARD}
        id="notfound-back-home-link"
        className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-violet-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-400"
      >
        ← Back to Dashboard
      </Link>
    </div>
  )
}
