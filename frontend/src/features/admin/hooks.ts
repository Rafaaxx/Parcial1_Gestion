/**
 * Custom hooks for Admin module using TanStack Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getResumen,
  getVentas,
  getProductosTop,
  getPedidosPorEstado,
  getUsuarios,
  updateUsuario,
  updateUsuarioEstado,
} from './api'
import type {
  UpdateUsuarioRequest,
  UpdateUsuarioEstadoRequest,
} from './types'

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const adminKeys = {
  all: ['admin'] as const,
  metrics: () => [...adminKeys.all, 'metrics'] as const,
  resumen: (desde?: string, hasta?: string) =>
    [...adminKeys.metrics(), 'resumen', { desde, hasta }] as const,
  ventas: (granularidad: string, desde?: string, hasta?: string) =>
    [...adminKeys.metrics(), 'ventas', { granularidad, desde, hasta }] as const,
  productosTop: (top: number, desde?: string, hasta?: string) =>
    [...adminKeys.metrics(), 'productos-top', { top, desde, hasta }] as const,
  pedidosPorEstado: (desde?: string, hasta?: string) =>
    [...adminKeys.metrics(), 'pedidos-estado', { desde, hasta }] as const,
  usuarios: () => [...adminKeys.all, 'usuarios'] as const,
  usuariosList: (params: Record<string, unknown>) =>
    [...adminKeys.usuarios(), 'list', params] as const,
}

// ═══════════════════════════════════════════════════════════════════════════
// Metrics Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get dashboard summary metrics
 */
export function useResumen(desde?: string, hasta?: string) {
  return useQuery({
    queryKey: adminKeys.resumen(desde, hasta),
    queryFn: () => getResumen(desde, hasta),
  })
}

/**
 * Get sales by time period
 */
export function useVentas(
  granularidad: 'dia' | 'semana' | 'mes' = 'dia',
  desde?: string,
  hasta?: string
) {
  return useQuery({
    queryKey: adminKeys.ventas(granularidad, desde, hasta),
    queryFn: () => getVentas(granularidad, desde, hasta),
  })
}

/**
 * Get top selling products
 */
export function useProductosTop(
  top: number = 10,
  desde?: string,
  hasta?: string
) {
  return useQuery({
    queryKey: adminKeys.productosTop(top, desde, hasta),
    queryFn: () => getProductosTop(top, desde, hasta),
  })
}

/**
 * Get orders grouped by state
 */
export function usePedidosPorEstado(desde?: string, hasta?: string) {
  return useQuery({
    queryKey: adminKeys.pedidosPorEstado(desde, hasta),
    queryFn: () => getPedidosPorEstado(desde, hasta),
  })
}

// ═══════════════════════════════════════════════════════════════════════════
// User Management Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * List users with pagination and filters
 */
export function useUsuarios(
  skip: number = 0,
  limit: number = 20,
  busqueda?: string,
  rol?: string,
  activo?: boolean
) {
  return useQuery({
    queryKey: adminKeys.usuariosList({ skip, limit, busqueda, rol, activo }),
    queryFn: () => getUsuarios(skip, limit, busqueda, rol, activo),
  })
}

/**
 * Update user data (name, email, roles)
 */
export function useUpdateUsuario() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      usuarioId,
      data,
    }: {
      usuarioId: number
      data: UpdateUsuarioRequest
    }) => updateUsuario(usuarioId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.usuarios() })
    },
  })
}

/**
 * Activate or deactivate a user
 */
export function useUpdateUsuarioEstado() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      usuarioId,
      data,
    }: {
      usuarioId: number
      data: UpdateUsuarioEstadoRequest
    }) => updateUsuarioEstado(usuarioId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.usuarios() })
    },
  })
}
