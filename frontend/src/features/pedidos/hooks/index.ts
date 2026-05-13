/**
 * Custom hooks for Pedidos (Orders) module
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getPedidos,
  getPedidoDetail,
  transicionarEstado,
  cancelarPedido,
} from '../api'
import { TransicionRequest } from '../types'

// Query keys
export const pedidoKeys = {
  all: ['pedidos'] as const,
  lists: () => [...pedidoKeys.all, 'list'] as const,
  list: (params: { skip?: number; limit?: number }) =>
    [...pedidoKeys.lists(), params] as const,
  details: () => [...pedidoKeys.all, 'detail'] as const,
  detail: (id: number) => [...pedidoKeys.details(), id] as const,
}

/**
 * Hook to fetch list of orders
 */
export function usePedidos(skip = 0, limit = 20) {
  return useQuery({
    queryKey: pedidoKeys.list({ skip, limit }),
    queryFn: () => getPedidos(skip, limit),
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
      allowed_roles: ['SISTEMA'],
      icon: '✓',
    },
    {
      label: 'Cancelar',
      nuevo_estado: 'CANCELADO' as EstadoPedido,
      requires_motivo: true,
      allowed_roles: ['CLIENT', 'ADMIN', 'PEDIDOS'],
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
      allowed_roles: ['ADMIN'],
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