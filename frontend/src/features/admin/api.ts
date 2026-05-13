/**
 * API integration for Admin module
 * Handles all HTTP calls to the backend admin endpoints
 */

import { apiClient } from '@/shared/http/client'
import type {
  ResumenMetricas,
  VentaPeriodo,
  ProductoTop,
  PedidoEstadoItem,
  UsuarioAdminListResponse,
  UsuarioAdmin,
  UpdateUsuarioRequest,
  UpdateUsuarioEstadoRequest,
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
// Dashboard Metrics
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get dashboard metrics summary
 * GET /api/v1/admin/metricas/resumen
 */
export async function getResumen(
  desde?: string,
  hasta?: string
): Promise<ResumenMetricas> {
  const params: Record<string, string> = {}
  if (desde) params.desde = desde
  if (hasta) params.hasta = hasta

  const response = await apiClient.get<ResumenMetricas>(
    `${API_BASE}${API_VERSION}/admin/metricas/resumen`,
    { params, headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Get sales by period
 * GET /api/v1/admin/metricas/ventas
 */
export async function getVentas(
  granularidad: 'dia' | 'semana' | 'mes' = 'dia',
  desde?: string,
  hasta?: string
): Promise<VentaPeriodo[]> {
  const params: Record<string, string> = { granularidad }
  if (desde) params.desde = desde
  if (hasta) params.hasta = hasta

  const response = await apiClient.get<VentaPeriodo[]>(
    `${API_BASE}${API_VERSION}/admin/metricas/ventas`,
    { params, headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Get top selling products
 * GET /api/v1/admin/metricas/productos-top
 */
export async function getProductosTop(
  top: number = 10,
  desde?: string,
  hasta?: string
): Promise<ProductoTop[]> {
  const params: Record<string, string | number> = { top }
  if (desde) params.desde = desde
  if (hasta) params.hasta = hasta

  const response = await apiClient.get<ProductoTop[]>(
    `${API_BASE}${API_VERSION}/admin/metricas/productos-top`,
    { params, headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Get orders by state
 * GET /api/v1/admin/metricas/pedidos-por-estado
 */
export async function getPedidosPorEstado(
  desde?: string,
  hasta?: string
): Promise<PedidoEstadoItem[]> {
  const params: Record<string, string> = {}
  if (desde) params.desde = desde
  if (hasta) params.hasta = hasta

  const response = await apiClient.get<PedidoEstadoItem[]>(
    `${API_BASE}${API_VERSION}/admin/metricas/pedidos-por-estado`,
    { params, headers: getAuthHeaders() }
  )
  return response.data
}

// ═══════════════════════════════════════════════════════════════════════════
// User Management
// ═══════════════════════════════════════════════════════════════════════════

/**
 * List users with pagination, search, and filters
 * GET /api/v1/admin/usuarios
 */
export async function getUsuarios(
  skip: number = 0,
  limit: number = 20,
  busqueda?: string,
  rol?: string,
  activo?: boolean
): Promise<UsuarioAdminListResponse> {
  const params: Record<string, string | number | boolean> = { skip, limit }
  if (busqueda) params.busqueda = busqueda
  if (rol) params.rol = rol
  if (activo !== undefined) params.activo = activo

  const response = await apiClient.get<UsuarioAdminListResponse>(
    `${API_BASE}${API_VERSION}/admin/usuarios`,
    { params, headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Update user data (name, email, roles)
 * PUT /api/v1/admin/usuarios/{id}
 */
export async function updateUsuario(
  usuarioId: number,
  data: UpdateUsuarioRequest
): Promise<UsuarioAdmin> {
  const response = await apiClient.put<UsuarioAdmin>(
    `${API_BASE}${API_VERSION}/admin/usuarios/${usuarioId}`,
    data,
    { headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Activate or deactivate a user
 * PATCH /api/v1/admin/usuarios/{id}/estado
 */
export async function updateUsuarioEstado(
  usuarioId: number,
  data: UpdateUsuarioEstadoRequest
): Promise<UsuarioAdmin> {
  const response = await apiClient.patch<UsuarioAdmin>(
    `${API_BASE}${API_VERSION}/admin/usuarios/${usuarioId}/estado`,
    data,
    { headers: getAuthHeaders() }
  )
  return response.data
}
