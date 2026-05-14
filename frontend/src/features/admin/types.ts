/**
 * Types for Admin module — metrics and user management
 */

// ── Dashboard Metrics ──────────────────────────────────────────────────────

export interface ResumenMetricas {
  total_ventas: string
  cantidad_pedidos: number
  pedidos_por_estado: PedidoEstadoItem[]
  usuarios_registrados: number
  productos_mas_vendidos: ProductoTop[]
}

export interface PedidoEstadoItem {
  estado: string
  cantidad: number
  porcentaje: number
}

export interface ProductoTop {
  producto_id: number
  nombre: string
  cantidad_total: number
  ingreso_total: string
}

export interface VentaPeriodo {
  periodo: string
  monto_total: string
  cantidad_pedidos: number
}

// ── User Management ───────────────────────────────────────────────────────

export interface UsuarioAdmin {
  id: number
  nombre: string
  email: string
  roles: string[]
  activo: boolean
  creado_en: string | null
  ultimo_login: string | null
}

export interface UsuarioAdminListResponse {
  items: UsuarioAdmin[]
  total: number
  skip: number
  limit: number
}

export interface UpdateUsuarioRequest {
  nombre?: string
  email?: string
  roles_codes?: string[]
}

export interface UpdateUsuarioEstadoRequest {
  activo: boolean
}

export interface UsuarioAdminFilters {
  busqueda?: string
  rol?: string
  activo?: boolean
}