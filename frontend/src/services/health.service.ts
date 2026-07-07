/**
 * Health service — API calls for the /health endpoint.
 *
 * These functions are defined here but NOT called anywhere in Module 1B.
 * They will be wired up in Module 1C when the Dashboard fetches live status.
 *
 * Pattern:
 *   All service functions return the unwrapped data (not the AxiosResponse)
 *   so callers deal only with domain types, never with HTTP internals.
 */

import type { HealthResponse } from '@/types'
import { apiClient } from './api'

/**
 * Fetch the backend health status.
 *
 * @returns `HealthResponse` — `{ status: 'healthy', service: 'backend' }`
 * @throws `ApiError` when the request fails or the backend is unreachable.
 */
export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/health')
  return data
}
