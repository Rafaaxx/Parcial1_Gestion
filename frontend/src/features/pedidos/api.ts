/**
 * API integration for Pedidos (Orders)
 * Handles all HTTP calls to the backend orders endpoints
 */

import { apiClient } from '@/shared/http/client'
import { useAuthStore } from '@/features/auth/store'
import {
  PedidosResponse,
  Pedido,
  TransicionRequest,
  TransicionResponse,
  PedidoFilters,
} from './types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_VERSION = '/api/v1'

/**
 * Helper to get auth token directly from localStorage (bypass Zustand hydration issues)
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
  } catch (e) {
    console.error('[DEBUG] Error reading token:', e)
  }
  return {}
}

/**
 * Get list of orders with pagination and optional filters
 * GET /api/v1/pedidos
 *
 * CLIENT role: returns only own orders
 * ADMIN/PEDIDOS roles: returns all orders
 */
export async function getPedidos(
  skip = 0,
  limit = 20,
  filtros?: PedidoFilters
): Promise<PedidosResponse> {
  try {
    const params: Record<string, string | number> = { skip, limit }
    
    // Add filters if provided
    if (filtros) {
      if (filtros.estado) params.estado = filtros.estado
      if (filtros.desde) params.desde = filtros.desde
      if (filtros.hasta) params.hasta = filtros.hasta
      if (filtros.busqueda) params.busqueda = filtros.busqueda
      if (filtros.solo_mios) params.solo_mios = String(filtros.solo_mios)
    }

    const response = await apiClient.get<PedidosResponse>(
      `${API_BASE}${API_VERSION}/pedidos`,
      { 
        params,
        headers: getAuthHeaders(),
      }
    )
    return response.data
  } catch (error: unknown) {
    const err = error as { response?: { status?: number; data?: { detail?: string } }; message?: string }
    const status = err.response?.status
    const message = err.response?.data?.detail || err.message

    if (status === 403) {
      throw new Error('No tienes permisos para ver pedidos')
    }
    if (status === 500) {
      throw new Error('Error del servidor al obtener pedidos')
    }

    throw new Error(message || 'Error al obtener pedidos')
  }
}

/**
 * Get order detail by ID
 * GET /api/v1/pedidos/{id}
 */
export async function getPedidoDetail(id: number): Promise<Pedido> {
  try {
    const response = await apiClient.get<Pedido>(
      `${API_BASE}${API_VERSION}/pedidos/${id}`,
      { headers: getAuthHeaders() }
    )
    return response.data
  } catch (error: unknown) {
    const err = error as { response?: { status?: number; data?: { detail?: string } }; message?: string }
    const status = err.response?.status

    if (status === 404) {
      throw new Error('Pedido no encontrado')
    }
    if (status === 403) {
      throw new Error('No tienes permisos para ver este pedido')
    }
    if (status === 500) {
      throw new Error('Error del servidor al obtener el pedido')
    }

    throw new Error(err.response?.data?.detail || err.message || 'Error al obtener pedido')
  }
}

/**
 * Transition order to a new state
 * PATCH /api/v1/pedidos/{id}/estado
 */
export async function transicionarEstado(
  pedidoId: number,
  data: TransicionRequest
): Promise<TransicionResponse> {
  try {
    const response = await apiClient.patch<TransicionResponse>(
      `${API_BASE}${API_VERSION}/pedidos/${pedidoId}/estado`,
      data,
      { headers: getAuthHeaders() }
    )
    return response.data
  } catch (error: unknown) {
    const err = error as { response?: { status?: number; data?: { detail?: string } }; message?: string }
    const status = err.response?.status
    const message = err.response?.data?.detail || err.message

    if (status === 404) {
      throw new Error('Pedido no encontrado')
    }
    if (status === 422) {
      throw new Error(message || 'Transición no válida')
    }
    if (status === 403) {
      throw new Error('No tienes permisos para esta transición')
    }
    if (status === 500) {
      throw new Error('Error del servidor al cambiar estado')
    }

    throw new Error(message || 'Error al cambiar estado del pedido')
  }
}

/**
 * Cancel an order (convenience endpoint)
 * DELETE /api/v1/pedidos/{id}?motivo=...
 *
 * CLIENT: can cancel own PENDIENTE orders
 * ADMIN/PEDIDOS: can cancel PENDIENTE or CONFIRMADO orders
 */
export async function cancelarPedido(
  pedidoId: number,
  motivo: string
): Promise<TransicionResponse> {
  try {
    const response = await apiClient.delete<TransicionResponse>(
      `${API_BASE}${API_VERSION}/pedidos/${pedidoId}`,
      { 
        params: { motivo },
        headers: getAuthHeaders(),
      }
    )
    return response.data
  } catch (error: unknown) {
    const err = error as { response?: { status?: number; data?: { detail?: string } }; message?: string }
    const status = err.response?.status
    const message = err.response?.data?.detail || err.message

    if (status === 404) {
      throw new Error('Pedido no encontrado')
    }
    if (status === 422) {
      throw new Error(message || 'No se puede cancelar el pedido')
    }
    if (status === 403) {
      throw new Error('No tienes permisos para cancelar este pedido')
    }
    if (status === 500) {
      throw new Error('Error del servidor al cancelar pedido')
    }

    throw new Error(message || 'Error al cancelar pedido')
  }
}

/**
 * Get order state transition history
 * GET /api/v1/pedidos/{id}/historial
 */
export async function getPedidoHistorial(pedidoId: number) {
  try {
    const response = await apiClient.get(
      `${API_BASE}${API_VERSION}/pedidos/${pedidoId}/historial`,
      { headers: getAuthHeaders() }
    )
    return response.data
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } }; message?: string }
    throw new Error(
      err.response?.data?.detail || 'Error al obtener historial'
    )
  }
}

/**
 * Payment status types
 */
export type PaymentStatus = 'approved' | 'rejected' | 'in_process' | 'pending' | 'none'

/**
 * Payment info from MercadoPago
 */
export interface PagoInfo {
  id: number
  pedido_id: number
  monto: number
  mp_payment_id: string | null
  mp_status: string | null
  external_reference: string
  idempotency_key: string
  created_at: string
  updated_at: string
}

/**
 * Get payment info by order ID
 * GET /api/v1/pagos/{pedido_id}
 */
export async function getPagoByPedidoId(pedidoId: number): Promise<PagoInfo | null> {
  try {
    const response = await apiClient.get<PagoInfo>(
      `${API_BASE}${API_VERSION}/pagos/${pedidoId}`,
      { headers: getAuthHeaders() }
    )
    return response.data
  } catch (error: unknown) {
    const err = error as { response?: { status?: number; data?: { detail?: string } }; message?: string }
    const status = err.response?.status

    // 404 means no payment record exists (e.g., cash payment)
    if (status === 404) {
      return null
    }

    throw new Error(
      err.response?.data?.detail || 'Error al obtener información de pago'
    )
  }
}