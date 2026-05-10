/**
 * HTTP interceptors for token management and error handling
 */

import { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { apiClient } from './client'
import { useAuthStore } from '@/features/auth/store'
import { useUIStore } from '@/features/ui/store'

/**
 * Request interceptor: add Bearer token to Authorization header
 */
export const setupRequestInterceptor = () => {
  apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  })
}

// Singleton pattern for refresh token flow
let refreshPromise: Promise<void> | null = null

interface QueuedRequest {
  resolve: (value: unknown) => void
  reject: (reason: unknown) => void
  config: InternalAxiosRequestConfig
}

let failedQueue: QueuedRequest[] = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject, config }) => {
    if (error) {
      reject(error)
    } else if (token) {
      config.headers.Authorization = `Bearer ${token}`
      resolve(apiClient(config))
    }
  })
  failedQueue = []
}

/**
 * Response interceptor: handle 401 errors and token refresh
 */
export const setupResponseInterceptor = () => {
  apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean
      }

      // Map HTTP errors to toast messages
      const status = error.response?.status

      if (status && status !== 401) {
        const toastMessage = getErrorMessage(status)
        if (toastMessage) {
          useUIStore.getState().showToast({
            id: `http-error-${status}-${Date.now()}`,
            type: 'error',
            message: toastMessage,
            duration: 5000,
          })
        }
      }

      // Handle 401 Unauthorized
      if (status === 401 && !originalRequest._retry) {
        // Don't intercept the refresh endpoint itself
        if (originalRequest.url?.includes('/auth/refresh')) {
          return Promise.reject(error)
        }

        originalRequest._retry = true

        const { refreshToken, logout } = useAuthStore.getState()

        if (!refreshToken) {
          logout()
          window.location.href = '/auth/login'
          return Promise.reject(error)
        }

        // If no refresh in progress, start one
        if (!refreshPromise) {
          refreshPromise = (async () => {
            try {
              const response = await apiClient.post('/auth/refresh', {
                refresh_token: refreshToken,
              })
              const { access_token: newToken, refresh_token: newRefreshToken } = response.data
              useAuthStore.getState().setTokens(newToken, newRefreshToken)
              processQueue(null, newToken)
            } catch (refreshError) {
              processQueue(refreshError, null)
              logout()
              window.location.href = '/auth/login'
              throw refreshError
            } finally {
              refreshPromise = null
            }
          })()
        }

        // Queue the failed request
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve,
            reject,
            config: originalRequest,
          })
        })
      }

      return Promise.reject(error)
    }
  )
}

function getErrorMessage(status: number): string | null {
  switch (status) {
    case 403:
      return 'No tenés permisos para esta acción'
    case 404:
      return 'Recurso no encontrado'
    case 429:
      return 'Demasiadas solicitudes, esperá un momento'
    case 500:
    case 502:
    case 503:
      return 'Error interno, intentá de nuevo más tarde'
    default:
      if (status >= 500) {
        return 'Error interno, intentá de nuevo más tarde'
      }
      return null
  }
}

// Setup interceptors on module import
setupRequestInterceptor()
setupResponseInterceptor()
