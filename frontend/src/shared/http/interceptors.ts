/**
 * HTTP interceptors for token management and error handling
 */

import { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { apiClient } from './client'
import { useAuthStore } from '@/features/auth/store'

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

      // Handle 401 Unauthorized
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        const { refreshToken, setTokens, logout } = useAuthStore.getState()

        if (refreshToken) {
          try {
            // TODO: Call refresh endpoint in CHANGE-01
            // const response = await apiClient.post('/auth/refresh', { refreshToken })
            // setTokens(response.data.token, response.data.refreshToken)
            // return apiClient(originalRequest)
          } catch (refreshError) {
            logout()
            // TODO: Redirect to login in CHANGE-02
          }
        } else {
          logout()
          // TODO: Redirect to login in CHANGE-02
        }
      }

      return Promise.reject(error)
    }
  )
}

// Setup interceptors on module import
setupRequestInterceptor()
setupResponseInterceptor()
