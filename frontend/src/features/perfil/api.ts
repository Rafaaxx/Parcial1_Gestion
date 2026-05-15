/**
 * API integration for Perfil module
 * Handles all HTTP calls to the backend perfil endpoints
 */

import { apiClient } from '@/shared/http/client'
import type {
  PerfilData,
  PerfilUpdate,
  PasswordChange,
  PasswordChangeResponse,
} from './types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_VERSION = '/api/v1'

/**
 * Helper to get auth token from localStorage (bypass Zustand hydration issues)
 */
const getAuthHeaders = () => {
  try {
    const stored = localStorage.getItem('food-store-auth')
    if (stored) {
      const parsed = JSON.parse(stored)
      const token = parsed.state?.token
      if (token) {
        return { Authorization: `Bearer ${token}` }
      }
    }
  } catch {
    // ignore
  }
  return {}
}

// ═══════════════════════════════════════════════════════════════════════════
// Profile CRUD
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get the authenticated user's profile
 * GET /api/v1/perfil
 */
export async function getPerfil(): Promise<PerfilData> {
  const response = await apiClient.get<PerfilData>(
    `${API_BASE}${API_VERSION}/perfil`,
    { headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Update profile fields (nombre, apellido, telefono)
 * PUT /api/v1/perfil
 * Email is immutable — cannot be changed
 */
export async function updatePerfil(data: PerfilUpdate): Promise<PerfilData> {
  const response = await apiClient.put<PerfilData>(
    `${API_BASE}${API_VERSION}/perfil`,
    data,
    { headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Change password — revokes all refresh tokens on success
 * PUT /api/v1/perfil/password
 */
export async function changePassword(
  data: PasswordChange
): Promise<PasswordChangeResponse> {
  const response = await apiClient.put<PasswordChangeResponse>(
    `${API_BASE}${API_VERSION}/perfil/password`,
    data,
    { headers: getAuthHeaders() }
  )
  return response.data
}
