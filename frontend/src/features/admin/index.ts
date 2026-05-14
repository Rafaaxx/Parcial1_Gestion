/**
 * Admin module exports
 */

export * from './types'
export * from './api'
export * from './hooks'

// Re-export API functions for convenience
export type {
  ProductoAdmin,
  ProductoListResponse,
  CreateProductoRequest,
  UpdateProductoRequest,
  CategoriaAdmin,
  CategoriaListResponse,
  PedidoAdmin,
  PedidoListResponse,
  IngredienteAdmin,
  IngredienteListResponse,
} from './api'