/**
 * RootLayout — the application shell.
 *
 * Structure:
 *   ┌─────────────────────────────┐
 *   │  Sidebar (fixed, 240px)     │  Header (h-14)         │
 *   │                             │─────────────────────── │
 *   │  nav items                  │  <Outlet />            │
 *   │                             │  (scrollable content)  │
 *   └─────────────────────────────┘────────────────────────┘
 *
 * The Outlet renders the current page component matched by React Router.
 * Sidebar and Header are mounted once and persist across page navigations.
 */

import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

export function RootLayout() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-950 text-slate-100">
      {/* Left sidebar — fixed width, full height */}
      <Sidebar />

      {/* Right panel — header + scrollable page content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />

        {/* Page content area */}
        <main
          id="main-content"
          className="flex-1 overflow-y-auto"
          role="main"
          aria-label="Page content"
        >
          <Outlet />
        </main>
      </div>
    </div>
  )
}
