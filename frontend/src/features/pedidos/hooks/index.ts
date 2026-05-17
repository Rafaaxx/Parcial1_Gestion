/**
 * Custom hooks for Pedidos (Orders) module
 */

import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getPedidos,
  getPedidoDetail,
  getPedidoHistorial,
  getPagoByPedidoId,
  transicionarEstado,
  cancelarPedido,
} from '../api'
import { TransicionRequest, PedidoFilters, HistorialEstado } from '../types'

// Get current user ID from auth storage
function getCurrentUserIdFromStorage(): number | null {
  try {
    const stored = localStorage.getItem('food-store-auth')
    if (stored) {
      const parsed = JSON.parse(stored)
      return parsed.state?.user?.id || null
    }
  } catch {
    // Ignore
  }
  return null
}

// Query keys
export const pedidoKeys = {
  all: ['pedidos'] as const,
  lists: () => [...pedidoKeys.all, 'list'] as const,
  list: (params: { skip?: number; limit?: number; filtros?: PedidoFilters; userId?: number | null }) =>
    [...pedidoKeys.lists(), params] as const,
  details: () => [...pedidoKeys.all, 'detail'] as const,
  detail: (id: number) => [...pedidoKeys.details(), id] as const,
}

/**
 * Hook to fetch list of orders with optional filters
 * Includes userId in queryKey to refetch when user changes
 */
export function usePedidos(skip = 0, limit = 20, filtros?: PedidoFilters) {
  const userId = getCurrentUserIdFromStorage()
  const queryClient = useQueryClient()
  
  // Effect to clear query cache when userId changes
  React.useEffect(() => {
    // Invalidate all pedido queries when userId changes
    queryClient.invalidateQueries({ queryKey: pedidoKeys.all })
  }, [userId, queryClient])
  
  return useQuery({
    queryKey: pedidoKeys.list({ skip, limit, filtros, userId }),
    queryFn: () => getPedidos(skip, limit, filtros),
    staleTime: 0,
  })
}

/**
 * Hook to fetch order detail
 */
export function usePedidoDetail(pedidoId: number) {
  return useQuery({
    queryKey: pedidoKeys.detail(pedidoId),
    queryFn: () => getPedidoDetail(pedidoId),
    enabled: pedidoId > 0,
  })
}

/**
 * Hook to fetch order state transition history
 */
export function usePedidoHistorial(pedidoId: number) {
  return useQuery<HistorialEstado[]>({
    queryKey: [...pedidoKeys.details(), pedidoId, 'historial'] as const,
    queryFn: () => getPedidoHistorial(pedidoId),
    enabled: pedidoId > 0,
  })
}

/**
 * Hook to fetch payment info for an order
 */
export function usePedidoPago(pedidoId: number) {
  return useQuery({
    queryKey: [...pedidoKeys.details(), pedidoId, 'pago'] as const,
    queryFn: () => getPagoByPedidoId(pedidoId),
    enabled: pedidoId > 0,
  })
}

/**
 * Hook to transition order state
 */
export function useTransicionEstado() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ pedidoId, data }: { pedidoId: number; data: TransicionRequest }) =>
      transicionarEstado(pedidoId, data),
    onSuccess: () => {
      // Invalidate pedidos list and detail queries
      queryClient.invalidateQueries({ queryKey: pedidoKeys.lists() })
      queryClient.invalidateQueries({ queryKey: pedidoKeys.all })
    },
  })
}

/**
 * Hook to cancel an order
 */
export function useCancelarPedido() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ pedidoId, motivo }: { pedidoId: number; motivo: string }) =>
      cancelarPedido(pedidoId, motivo),
    onSuccess: () => {
      // Invalidate pedidos list and detail queries
      queryClient.invalidateQueries({ queryKey: pedidoKeys.lists() })
      queryClient.invalidateQueries({ queryKey: pedidoKeys.all })
    },
  })
}

/**
 * Helper hook to get available transitions based on current state and user role
 */
import { EstadoPedido, TransicionAction } from '../types'

const TRANSICIONES_POR_ESTADO: Record<string, TransicionAction[]> = {
  PENDIENTE: [
    {
      label: 'Confirmar',
      nuevo_estado: 'CONFIRMADO' as EstadoPedido,
      allowed_roles: ['ADMIN', 'PEDIDOS'],
      icon: '✓',
    },
    {
      label: 'Cancelar',
      nuevo_estado: 'CANCELADO' as EstadoPedido,
      requires_motivo: true,
      allowed_roles: ['ADMIN', 'PEDIDOS'],
      icon: '✕',
    },
  ],
  CONFIRMADO: [
    {
      label: 'En Preparación',
      nuevo_estado: 'EN_PREP' as EstadoPedido,
      allowed_roles: ['ADMIN', 'PEDIDOS'],
      icon: '🍕',
    },
    {
      label: 'Cancelar',
      nuevo_estado: 'CANCELADO' as EstadoPedido,
      requires_motivo: true,
      allowed_roles: ['ADMIN', 'PEDIDOS'],
      icon: '✕',
    },
  ],
  EN_PREP: [
    {
      label: 'En Camino',
      nuevo_estado: 'EN_CAMINO' as EstadoPedido,
      allowed_roles: ['ADMIN', 'PEDIDOS'],
      icon: '🚚',
    },
    {
      label: 'Cancelar',
      nuevo_estado: 'CANCELADO' as EstadoPedido,
      requires_motivo: true,
      allowed_roles: ['ADMIN', 'PEDIDOS'],
      icon: '✕',
    },
  ],
  EN_CAMINO: [
    {
      label: 'Entregado',
      nuevo_estado: 'ENTREGADO' as EstadoPedido,
      allowed_roles: ['ADMIN', 'PEDIDOS'],
      icon: '✅',
    },
  ],
  ENTREGADO: [],
  CANCELADO: [],
}

export function getTransicionesDisponibles(
  estadoActual: string,
  userRoles: string[]
): TransicionAction[] {
  const transiciones = TRANSICIONES_POR_ESTADO[estadoActual] || []
  return transiciones.filter((t) =>
    t.allowed_roles.some((role) => userRoles.includes(role))
  )
}