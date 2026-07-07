/**
 * Application-wide constants.
 *
 * Single source of truth for strings and configuration that appear in
 * multiple places. Avoids magic strings scattered across the codebase.
 */

// ---------------------------------------------------------------------------
// Application identity
// ---------------------------------------------------------------------------

export const APP_NAME = 'Enterprise GenAI Platform' as const
export const APP_VERSION = '1.0.0' as const

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

export const API_VERSION = 'v1' as const

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

export const ROUTES = {
  DASHBOARD: '/',
  // Future modules — placeholder paths for router scaffolding
  MODELS: '/models',
  DEPLOYMENTS: '/deployments',
  USAGE: '/usage',
  SETTINGS: '/settings',
} as const

// ---------------------------------------------------------------------------
// Navigation items
// ---------------------------------------------------------------------------
// Icons are imported inline to keep this file framework-free; the actual
// SVG components are injected by the Sidebar via the NavItem.icon field.
// This array drives the sidebar — no JSX here, only data.
// ---------------------------------------------------------------------------

import type { NavItem } from '@/types'

import DashboardIcon from '../components/icons/DashboardIcon'
import ModelsIcon from '../components/icons/ModelsIcon'
import DeployIcon from '../components/icons/DeployIcon'
import UsageIcon from '../components/icons/UsageIcon'
import SettingsIcon from '../components/icons/SettingsIcon'

export const PRIMARY_NAV_ITEMS: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: ROUTES.DASHBOARD,
    icon: DashboardIcon,
  },
  {
    id: 'models',
    label: 'Models',
    path: ROUTES.MODELS,
    icon: ModelsIcon,
  },
  {
    id: 'deployments',
    label: 'Deployments',
    path: ROUTES.DEPLOYMENTS,
    icon: DeployIcon,
  },
  {
    id: 'usage',
    label: 'Usage',
    path: ROUTES.USAGE,
    icon: UsageIcon,
  },
]

export const FOOTER_NAV_ITEMS: NavItem[] = [
  {
    id: 'settings',
    label: 'Settings',
    path: ROUTES.SETTINGS,
    icon: SettingsIcon,
    isFooter: true,
  },
]
