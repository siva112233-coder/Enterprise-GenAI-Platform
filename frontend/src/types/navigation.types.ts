/**
 * Navigation type definitions.
 *
 * Describes the shape of a navigation item used in the Sidebar.
 * Keeping this separate from component code allows easy extension
 * (e.g., adding roles, badges, sub-items) without touching layout files.
 */

import type { ComponentType } from 'react'

export interface NavItem {
  /** Unique identifier — used as React key and for active-state detection. */
  id: string
  /** Display label shown in the sidebar. */
  label: string
  /** React Router path this item links to. */
  path: string
  /** Lucide-compatible icon component (or any SVG component). */
  icon: ComponentType<{ className?: string }>
  /** Optional badge count — e.g. for notifications or pending items. */
  badge?: number
  /** When true, the item appears in the footer section of the sidebar. */
  isFooter?: boolean
}

export interface NavSection {
  title?: string
  items: NavItem[]
}
