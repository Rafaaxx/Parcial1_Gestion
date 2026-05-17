/**
 * Types for Pedido (Order) module
 */

export type EstadoPedido =
  | 'PENDIENTE'
  | 'CONFIRMADO'
  | 'EN_PREP'
  | 'EN_CAMINO'
  | 'ENTREGADO'
  | 'CANCELADO'

export interface ClienteInfo {
  id: number
  nombre?: string | null
  email: string
}

export interface DetallePedido {
  id: number
  producto_id: number
  nombre_snapshot: string
  precio_snapshot: number
  cantidad: number
  personalizacion?: number[] | null
  created_at: string
}

export interface HistorialEstado {
  id: number
  estado_desde: string | null
  estado_hacia: string
  observacion?: string | null
  usuario_id?: number | null
  created_at: string
}

export interface Pedido {
  id: number
  usuario_id: number
  estado_codigo: string
  total: number
  costo_envio: number
  forma_pago_codigo: string
  direccion_id?: number | null
  notas?: string | null
  detalles: DetallePedido[]
  historial: HistorialEstado[]
  created_at: string
  updated_at: string
  cliente?: ClienteInfo | null
}

export interface PedidoListItem {
  id: number
  usuario_id: number
  estado_codigo: string
  total: number
  costo_envio: number
  created_at: string
  cliente?: ClienteInfo | null
}

export interface PedidosResponse {
  items: PedidoListItem[]
  total: number
  skip: number
  limit: number
}

// Filter types for order management
export interface PedidoFilters {
  estado?: string
  desde?: string
  hasta?: string
  busqueda?: string
  solo_mios?: boolean
}

export interface TransicionRequest {
  nuevo_estado: EstadoPedido
  motivo?: string
}

export interface TransicionResponse {
  id: number
  estado_codigo: string
  mensaje: string
}

// UI helper types
export interface TransicionAction {
  label: string
  nuevo_estado: EstadoPedido
  requires_motivo?: boolean
  allowed_roles: string[]
  icon?: string
}

export const ESTADOS_TERMINALES: EstadoPedido[] = ['ENTREGADO', 'CANCELADO']

export function esEstadoTerminal(estado: string): boolean {
  return ESTADOS_TERMINALES.includes(estado as EstadoPedido)
}

export const ESTADO_LABELS: Record<EstadoPedido, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PREP: 'En Preparación',
  EN_CAMINO: 'En Camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
}

export const ESTADO_COLORS: Record<EstadoPedido, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  CONFIRMADO: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  EN_PREP: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  EN_CAMINO: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  ENTREGADO: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  CANCELADO: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
}