/**
 * Axios instance — central HTTP client for all API requests.
 *
 * Configuration:
 * - Base URL driven by `VITE_API_BASE_URL` environment variable.
 * - Default timeout: 15 seconds.
 * - Request interceptor: attaches auth tokens (stub for future auth module).
 * - Response interceptor: normalises error shape to `ApiError`.
 *
 * Usage:
 *   import { apiClient } from '@/services/api'
 *   const data = await apiClient.get<HealthResponse>('/health')
 */

import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'

import type { ApiError } from '@/types'

// ---------------------------------------------------------------------------
// Instance
// ---------------------------------------------------------------------------

const baseURL: string =
  import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 15_000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// ---------------------------------------------------------------------------
// Request interceptor — attach auth token when available
// ---------------------------------------------------------------------------

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    // TODO (Module 1C — Auth): retrieve token from store and attach here.
    // const token = useAuthStore.getState().accessToken
    // if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error: unknown) => Promise.reject(error),
)

// ---------------------------------------------------------------------------
// Response interceptor — normalise error shape
// ---------------------------------------------------------------------------

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response) {
      const apiError: ApiError = {
        detail:
          (error.response.data as { detail?: string }).detail ??
          'An unexpected error occurred.',
        status_code: error.response.status,
      }
      return Promise.reject(apiError)
    }
    return Promise.reject(error)
  },
)
