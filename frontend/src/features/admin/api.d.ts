/**
 * API integration for Admin module
 * Handles all HTTP calls to the backend admin endpoints
 */
import type { ResumenMetricas, VentaPeriodo, ProductoTop, PedidoEstadoItem, UsuarioAdminListResponse, UsuarioAdmin, UpdateUsuarioRequest, UpdateUsuarioEstadoRequest } from './types';
/**
 * Get dashboard metrics summary
 * GET /api/v1/admin/metricas/resumen
 */
export declare function getResumen(desde?: string, hasta?: string): Promise<ResumenMetricas>;
/**
 * Get sales by period
 * GET /api/v1/admin/metricas/ventas
 */
export declare function getVentas(granularidad?: 'dia' | 'semana' | 'mes', desde?: string, hasta?: string): Promise<VentaPeriodo[]>;
/**
 * Get top selling products
 * GET /api/v1/admin/metricas/productos-top
 */
export declare function getProductosTop(top?: number, desde?: string, hasta?: string): Promise<ProductoTop[]>;
/**
 * Get orders by state
 * GET /api/v1/admin/metricas/pedidos-por-estado
 */
export declare function getPedidosPorEstado(desde?: string, hasta?: string): Promise<PedidoEstadoItem[]>;
/**
 * List users with pagination, search, and filters
 * GET /api/v1/admin/usuarios
 */
export declare function getUsuarios(skip?: number, limit?: number, busqueda?: string, rol?: string, activo?: boolean): Promise<UsuarioAdminListResponse>;
/**
 * Update user data (name, email, roles)
 * PUT /api/v1/admin/usuarios/{id}
 */
export declare function updateUsuario(usuarioId: number, data: UpdateUsuarioRequest): Promise<UsuarioAdmin>;
/**
 * Activate or deactivate a user
 * PATCH /api/v1/admin/usuarios/{id}/estado
 */
export declare function updateUsuarioEstado(usuarioId: number, data: UpdateUsuarioEstadoRequest): Promise<UsuarioAdmin>;
//# sourceMappingURL=api.d.ts.map