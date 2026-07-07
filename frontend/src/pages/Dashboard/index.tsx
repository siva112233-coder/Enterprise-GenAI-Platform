/**
 * Dashboard page — Module 1B entry view.
 *
 * Displays:
 *   - Platform name heading: "Enterprise GenAI Platform"
 *   - System status: "System Healthy" (static — no API call in Module 1B)
 *
 * Module 1C will replace the static badge with a live `fetchHealth()` call.
 */

import { Badge } from '@/components/ui'
import { usePageTitle } from '@/hooks/usePageTitle'
import { APP_NAME } from '@/utils/constants'

export default function DashboardPage() {
  usePageTitle('Dashboard')

  return (
    <div className="min-h-full px-8 py-10">
      {/* ------------------------------------------------------------------ */}
      {/* Page header                                                         */}
      {/* ------------------------------------------------------------------ */}
      <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            {APP_NAME}
          </h1>
          <p className="text-sm text-slate-400">
            Unified gateway for all AI model deployments and usage analytics.
          </p>
        </div>

        {/* System status badge — static in Module 1B */}
        <div className="flex items-center gap-2 rounded-xl border border-white/8 bg-slate-900 px-4 py-3">
          <Badge variant="healthy" withDot>
            System Healthy
          </Badge>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Coming-soon placeholder grid                                        */}
      {/* Widgets will be added in future modules — grid scaffolded here.    */}
      {/* ------------------------------------------------------------------ */}
      <div
        className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Dashboard metrics"
      >
        {PLACEHOLDER_CARDS.map((card) => (
          <PlaceholderCard key={card.id} {...card} />
        ))}
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Module 1B notice                                                    */}
      {/* ------------------------------------------------------------------ */}
      <div className="mt-10 rounded-xl border border-dashed border-white/10 bg-slate-900/50 p-8 text-center">
        <p className="text-sm font-medium text-slate-400">
          Dashboard widgets will be added in future modules.
        </p>
        <p className="mt-1 text-xs text-slate-600">
          Module 1B — Foundation architecture complete.
        </p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Placeholder metric cards — scaffold for future widgets
// ---------------------------------------------------------------------------

interface PlaceholderCardData {
  id: string
  label: string
  description: string
}

const PLACEHOLDER_CARDS: PlaceholderCardData[] = [
  {
    id: 'total-requests',
    label: 'Total Requests',
    description: 'API calls across all models',
  },
  {
    id: 'active-models',
    label: 'Active Models',
    description: 'Currently deployed',
  },
  {
    id: 'avg-latency',
    label: 'Avg Latency',
    description: 'P95 response time',
  },
  {
    id: 'error-rate',
    label: 'Error Rate',
    description: '4xx / 5xx over 24 h',
  },
]

function PlaceholderCard({ id, label, description }: PlaceholderCardData) {
  return (
    <div
      id={`metric-card-${id}`}
      className="flex flex-col gap-3 rounded-xl border border-white/8 bg-slate-900 p-5"
    >
      <div className="h-8 w-24 animate-pulse rounded-md bg-white/5" />
      <div>
        <p className="text-sm font-semibold text-slate-200">{label}</p>
        <p className="text-xs text-slate-500">{description}</p>
      </div>
    </div>
  )
}
