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
  getProductos,
  getProductoById,
  createProducto,
  updateProducto,
  deleteProducto,
  updateProductoStock,
  getCategorias,
  createCategoria,
  updateCategoria,
  deleteCategoria,
  getPedidos,
  updatePedidoEstado,
  getIngredientes,
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

// ═══════════════════════════════════════════════════════════════════════════
// Products Hooks
// ═══════════════════════════════════════════════════════════════════════════

export const adminProductsKeys = {
  all: ['admin-products'] as const,
  list: (params: Record<string, unknown>) => [...adminProductsKeys.all, 'list', params] as const,
  detail: (id: number) => [...adminProductsKeys.all, 'detail', id] as const,
}

export function useProductos(
  skip: number = 0,
  limit: number = 50,
  categoria_id?: number,
  disponible?: boolean
) {
  return useQuery({
    queryKey: adminProductsKeys.list({ skip, limit, categoria_id, disponible }),
    queryFn: () => getProductos(skip, limit, categoria_id, disponible),
  })
}

export function useProductoById(id: number) {
  return useQuery({
    queryKey: adminProductsKeys.detail(id),
    queryFn: () => getProductoById(id),
    enabled: !!id,
  })
}

export function useCreateProducto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Parameters<typeof createProducto>[0]) => createProducto(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminProductsKeys.all })
    },
  })
}

export function useUpdateProducto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateProducto>[1] }) =>
      updateProducto(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminProductsKeys.all })
    },
  })
}

export function useDeleteProducto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => deleteProducto(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminProductsKeys.all })
    },
  })
}

export function useUpdateProductoStock() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, stock_cantidad }: { id: number; stock_cantidad: number }) =>
      updateProductoStock(id, stock_cantidad),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminProductsKeys.all })
    },
  })
}

// ═══════════════════════════════════════════════════════════════════════════
// Categories Hooks
// ═══════════════════════════════════════════════════════════════════════════

export const adminCategoriasKeys = {
  all: ['admin-categorias'] as const,
  list: () => [...adminCategoriasKeys.all, 'list'] as const,
}

export function useCategorias(skip: number = 0, limit: number = 100) {
  return useQuery({
    queryKey: adminCategoriasKeys.list(),
    queryFn: () => getCategorias(skip, limit),
  })
}

export function useCreateCategoria() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Parameters<typeof createCategoria>[0]) => createCategoria(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminCategoriasKeys.all })
    },
  })
}

export function useUpdateCategoria() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateCategoria>[1] }) =>
      updateCategoria(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminCategoriasKeys.all })
    },
  })
}

export function useDeleteCategoria() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => deleteCategoria(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminCategoriasKeys.all })
    },
  })
}

// ═══════════════════════════════════════════════════════════════════════════
// Orders Hooks
// ═══════════════════════════════════════════════════════════════════════════

export const adminPedidosKeys = {
  all: ['admin-pedidos'] as const,
  list: (params: Record<string, unknown>) => [...adminPedidosKeys.all, 'list', params] as const,
}

export function usePedidos(skip: number = 0, limit: number = 50, estado?: string) {
  return useQuery({
    queryKey: adminPedidosKeys.list({ skip, limit, estado }),
    queryFn: () => getPedidos(skip, limit, estado),
  })
}

export function useUpdatePedidoEstado() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, nuevo_estado }: { id: number; nuevo_estado: string }) =>
      updatePedidoEstado(id, nuevo_estado),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminPedidosKeys.all })
    },
  })
}

// ═══════════════════════════════════════════════════════════════════════════
// Ingredients Hooks
// ═══════════════════════════════════════════════════════════════════════════

export const adminIngredientesKeys = {
  all: ['admin-ingredientes'] as const,
  list: () => [...adminIngredientesKeys.all, 'list'] as const,
}

export function useIngredientes() {
  return useQuery({
    queryKey: adminIngredientesKeys.list(),
    queryFn: () => getIngredientes(),
  })
}