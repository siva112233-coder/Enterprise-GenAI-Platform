/**
 * usePageTitle — sets the document title on mount.
 *
 * Appends the app name as a suffix so every tab reads:
 *   "Dashboard | Enterprise GenAI Platform"
 *
 * @param title - The page-specific part of the title.
 *
 * @example
 * usePageTitle('Dashboard')
 * // document.title === 'Dashboard | Enterprise GenAI Platform'
 */

import { useEffect } from 'react'
import { APP_NAME } from '@/utils/constants'

export function usePageTitle(title: string): void {
  useEffect(() => {
    const previous = document.title
    document.title = `${title} | ${APP_NAME}`

    return () => {
      document.title = previous
    }
  }, [title])
}
