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

// ═══════════════════════════════════════════════════════════════════════════
// Products (Catalogo)
// ═══════════════════════════════════════════════════════════════════════════

export interface ProductoAdmin {
  id: number
  nombre: string
  descripcion: string
  precio_base: number
  disponible: boolean
  stock_cantidad: number
  categoria_id: number
  categoria_nombre?: string
  creado_en: string
  actualizado_en: string
}

export interface ProductoListResponse {
  items: ProductoAdmin[]
  total: number
  skip: number
  limit: number
}

export interface CreateProductoRequest {
  nombre: string
  descripcion: string
  precio_base: number
  stock_cantidad: number
  disponible: boolean
  categoria_id: number
  ingrediente_ids?: number[]
}

export interface UpdateProductoRequest {
  nombre?: string
  descripcion?: string
  precio_base?: number
  stock_cantidad?: number
  disponible?: boolean
  categoria_id?: number
  ingrediente_ids?: number[]
}

/**
 * List products (stock/admin role)
 * GET /api/v1/productos?include_stock=true
 * include_stock=true is required for admin to receive stock_cantidad
 */
export async function getProductos(
  skip: number = 0,
  limit: number = 50,
  categoria_id?: number,
  disponible?: boolean,
  include_stock: boolean = true
): Promise<ProductoListResponse> {
  const params: Record<string, string | number | boolean> = { skip, limit, include_stock }
  if (categoria_id) params.categoria_id = categoria_id
  if (disponible !== undefined) params.disponible = disponible

  const response = await apiClient.get<ProductoListResponse>(
    `${API_BASE}${API_VERSION}/productos`,
    { params, headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Get product by ID
 * GET /api/v1/productos/{id}
 */
export async function getProductoById(id: number): Promise<ProductoAdmin> {
  const response = await apiClient.get<ProductoAdmin>(
    `${API_BASE}${API_VERSION}/productos/${id}`,
    { headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Create product
 * POST /api/v1/productos
 */
export async function createProducto(data: CreateProductoRequest): Promise<ProductoAdmin> {
  const response = await apiClient.post<ProductoAdmin>(
    `${API_BASE}${API_VERSION}/productos`,
    data,
    { headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Update product
 * PUT /api/v1/productos/{id}
 */
export async function updateProducto(
  id: number,
  data: UpdateProductoRequest
): Promise<ProductoAdmin> {
  const response = await apiClient.put<ProductoAdmin>(
    `${API_BASE}${API_VERSION}/productos/${id}`,
    data,
    { headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Delete product (soft delete)
 * DELETE /api/v1/productos/{id}
 */
export async function deleteProducto(id: number): Promise<void> {
  await apiClient.delete(
    `${API_BASE}${API_VERSION}/productos/${id}`,
    { headers: getAuthHeaders() }
  )
}

/**
 * Update product stock
 * PATCH /api/v1/productos/{id}/stock
 * Backend expects StockUpdate schema: { stock_cantidad: number }
 */
export async function updateProductoStock(
  id: number,
  stock_cantidad: number
): Promise<ProductoAdmin> {
  const response = await apiClient.patch<ProductoAdmin>(
    `${API_BASE}${API_VERSION}/productos/${id}/stock`,
    { stock_cantidad },
    { headers: getAuthHeaders() }
  )
  return response.data
}

// ═══════════════════════════════════════════════════════════════════════════
// Categories
// ═══════════════════════════════════════════════════════════════════════════

export interface CategoriaAdmin {
  id: number
  nombre: string
  descripcion: string
  activo: boolean
  padre_id: number | null
  hijo_ids: number[]
  creado_en: string
}

export interface CategoriaListResponse {
  items: CategoriaAdmin[]
  total: number
  skip: number
  limit: number
}

/**
 * Backend tree node shape (returned by GET /api/v1/categorias)
 */
interface BackendCategoriaTreeNode {
  id: number
  nombre: string
  descripcion: string | null
  parent_id: number | null
  created_at: string
  updated_at: string
  deleted_at: string | null
  subcategorias: BackendCategoriaTreeNode[]
}

/**
 * Backend read shape (returned by POST/PUT /api/v1/categorias)
 */
interface BackendCategoriaRead {
  id: number
  nombre: string
  descripcion: string | null
  parent_id: number | null
  created_at: string
  updated_at: string
  deleted_at: string | null
}

/**
 * Flatten a backend tree node + its descendants into CategoriaAdmin[]
 */
function flattenCategoriaTree(nodes: BackendCategoriaTreeNode[]): CategoriaAdmin[] {
  const result: CategoriaAdmin[] = []
  function walk(list: BackendCategoriaTreeNode[]) {
    for (const node of list) {
      result.push({
        id: node.id,
        nombre: node.nombre,
        descripcion: node.descripcion || '',
        activo: node.deleted_at === null,
        padre_id: node.parent_id,
        hijo_ids: node.subcategorias.map((c) => c.id),
        creado_en: node.created_at,
      })
      if (node.subcategorias.length > 0) walk(node.subcategorias)
    }
  }
  walk(nodes)
  return result
}

/** Map backend CategoriaRead → CategoriaAdmin */
function mapCategoriaRead(backend: BackendCategoriaRead): CategoriaAdmin {
  return {
    id: backend.id,
    nombre: backend.nombre,
    descripcion: backend.descripcion || '',
    activo: backend.deleted_at === null,
    padre_id: backend.parent_id,
    hijo_ids: [],  // POST/PUT responses don't include children
    creado_en: backend.created_at,
  }
}

/**
 * List categories
 * GET /api/v1/categorias (returns tree, we flatten it)
 */
export async function getCategorias(
  skip: number = 0,
  limit: number = 100
): Promise<CategoriaListResponse> {
  const response = await apiClient.get<BackendCategoriaTreeNode[]>(
    `${API_BASE}${API_VERSION}/categorias`,
    { params: { skip, limit }, headers: getAuthHeaders() }
  )
  const items = flattenCategoriaTree(response.data)
  return { items, total: items.length, skip, limit }
}

/**
 * Create category
 * POST /api/v1/categorias (backend expects parent_id, not padre_id)
 */
export async function createCategoria(data: {
  nombre: string
  descripcion: string
  padre_id?: number | undefined
}): Promise<CategoriaAdmin> {
  const payload = {
    nombre: data.nombre,
    descripcion: data.descripcion || null,
    parent_id: data.padre_id ?? null,
  }
  const response = await apiClient.post<BackendCategoriaRead>(
    `${API_BASE}${API_VERSION}/categorias`,
    payload,
    { headers: getAuthHeaders() }
  )
  return mapCategoriaRead(response.data)
}

/**
 * Update category
 * PUT /api/v1/categorias/{id} (backend expects parent_id, not padre_id)
 */
export async function updateCategoria(
  id: number,
  data: { nombre?: string; descripcion?: string; padre_id?: number }
): Promise<CategoriaAdmin> {
  const payload: Record<string, unknown> = {}
  if (data.nombre !== undefined) payload.nombre = data.nombre
  if (data.descripcion !== undefined) payload.descripcion = data.descripcion
  if (data.padre_id !== undefined) payload.parent_id = data.padre_id

  const response = await apiClient.put<BackendCategoriaRead>(
    `${API_BASE}${API_VERSION}/categorias/${id}`,
    payload,
    { headers: getAuthHeaders() }
  )
  return mapCategoriaRead(response.data)
}

/**
 * Delete category (soft delete)
 * DELETE /api/v1/categorias/{id}
 */
export async function deleteCategoria(id: number): Promise<void> {
  await apiClient.delete(
    `${API_BASE}${API_VERSION}/categorias/${id}`,
    { headers: getAuthHeaders() }
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Orders
// ═══════════════════════════════════════════════════════════════════════════

export interface PedidoAdmin {
  id: number
  usuario_id: number
  usuario_nombre: string
  estado: string
  total: string
  creado_en: string
  actualizado_en: string
  items: Array<{
    producto_id: number
    producto_nombre: string
    cantidad: number
    precio_unitario: string
    subtotal: string
  }>
  direccion?: {
    calle: string
    numero: number
    piso?: string
    ciudad: string
  }
}

export interface PedidoListResponse {
  items: PedidoAdmin[]
  total: number
  skip: number
  limit: number
}

/**
 * List orders (admin/pedidos role)
 * GET /api/v1/pedidos
 */
export async function getPedidos(
  skip: number = 0,
  limit: number = 50,
  estado?: string
): Promise<PedidoListResponse> {
  const params: Record<string, string | number> = { skip, limit }
  if (estado) params.estado = estado

  const response = await apiClient.get<PedidoListResponse>(
    `${API_BASE}${API_VERSION}/pedidos`,
    { params, headers: getAuthHeaders() }
  )
  return response.data
}

/**
 * Update order state
 * PATCH /api/v1/pedidos/{id}/estado
 */
export async function updatePedidoEstado(
  id: number,
  nuevo_estado: string
): Promise<PedidoAdmin> {
  const response = await apiClient.patch<PedidoAdmin>(
    `${API_BASE}${API_VERSION}/pedidos/${id}/estado`,
    { nuevo_estado },
    { headers: getAuthHeaders() }
  )
  return response.data
}

// ═══════════════════════════════════════════════════════════════════════════
// Ingredients
// ═══════════════════════════════════════════════════════════════════════════

export interface IngredienteAdmin {
  id: number
  nombre: string
  descripcion: string
  activo: boolean
  creado_en: string
}

export interface IngredienteListResponse {
  items: IngredienteAdmin[]
  total: number
}

/**
 * List ingredients
 * GET /api/v1/ingredientes
 */
export async function getIngredientes(): Promise<IngredienteListResponse> {
  const response = await apiClient.get<IngredienteListResponse>(
    `${API_BASE}${API_VERSION}/ingredientes`,
    { headers: getAuthHeaders() }
  )
  return response.data
}