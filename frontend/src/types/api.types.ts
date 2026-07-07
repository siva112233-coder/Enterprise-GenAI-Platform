/**
 * API response type definitions.
 *
 * These types model the JSON contract produced by the FastAPI backend.
 * Keep in sync with the Pydantic schemas in `backend/app/api/schemas/`.
 */

// ---------------------------------------------------------------------------
// Generic envelope types
// ---------------------------------------------------------------------------

/** Standard API error payload returned by FastAPI on 4xx / 5xx responses. */
export interface ApiError {
  detail: string
  status_code: number
}

/** Paginated list wrapper for collection endpoints. */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

/** Response shape for GET /api/v1/health */
export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  service: string
}

// ---------------------------------------------------------------------------
// System status (used by the Dashboard)
// ---------------------------------------------------------------------------

export type SystemStatus = HealthResponse['status']
