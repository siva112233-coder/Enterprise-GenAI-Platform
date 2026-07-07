/**
 * Router — application route tree.
 *
 * Uses `createBrowserRouter` (React Router v6 data API) for:
 *   - Nested layouts via `<Outlet />`
 *   - Route-level `handle.breadcrumb` metadata consumed by Header
 *   - Future: `loader` / `action` functions for data fetching
 *
 * Add a new page:
 *   1. Create `src/pages/YourPage/index.tsx`
 *   2. Add a nav item to `src/utils/constants.ts`
 *   3. Add a route object here
 */

import { createBrowserRouter } from 'react-router-dom'
import { lazy, Suspense } from 'react'

import { RootLayout } from '@/layouts/RootLayout'

// ---------------------------------------------------------------------------
// Lazy page imports — each page is a separate JS chunk (code splitting)
// ---------------------------------------------------------------------------

const DashboardPage = lazy(() => import('@/pages/Dashboard'))
const NotFoundPage = lazy(() => import('@/pages/NotFound'))

// ---------------------------------------------------------------------------
// Loading fallback
// ---------------------------------------------------------------------------

function PageLoader() {
  return (
    <div
      className="flex min-h-full items-center justify-center"
      aria-label="Loading page"
      role="status"
    >
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-white/10 border-t-violet-400" />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Route tree
// ---------------------------------------------------------------------------

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    // errorElement: <ErrorBoundaryPage />,  // TODO: add in Module 1C
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<PageLoader />}>
            <DashboardPage />
          </Suspense>
        ),
        handle: { breadcrumb: 'Dashboard' },
      },
      // ---------------------------------------------------------------
      // Placeholder routes — scaffold for future modules
      // Uncomment and add page components as modules are built.
      // ---------------------------------------------------------------
      // {
      //   path: 'models',
      //   element: <Suspense fallback={<PageLoader />}><ModelsPage /></Suspense>,
      //   handle: { breadcrumb: 'Models' },
      // },
      // {
      //   path: 'deployments',
      //   element: <Suspense fallback={<PageLoader />}><DeploymentsPage /></Suspense>,
      //   handle: { breadcrumb: 'Deployments' },
      // },
      // {
      //   path: 'usage',
      //   element: <Suspense fallback={<PageLoader />}><UsagePage /></Suspense>,
      //   handle: { breadcrumb: 'Usage' },
      // },
      // {
      //   path: 'settings',
      //   element: <Suspense fallback={<PageLoader />}><SettingsPage /></Suspense>,
      //   handle: { breadcrumb: 'Settings' },
      // },
      {
        path: '*',
        element: (
          <Suspense fallback={<PageLoader />}>
            <NotFoundPage />
          </Suspense>
        ),
      },
    ],
  },
])
