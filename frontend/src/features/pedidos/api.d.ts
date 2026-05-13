/**
 * API integration for Pedidos (Orders)
 * Handles all HTTP calls to the backend orders endpoints
 */
import { PedidosResponse, Pedido, TransicionRequest, TransicionResponse, PedidoFilters } from './types';
/**
 * Get list of orders with pagination and optional filters
 * GET /api/v1/pedidos
 *
 * CLIENT role: returns only own orders
 * ADMIN/PEDIDOS roles: returns all orders
 */
export declare function getPedidos(skip?: number, limit?: number, filtros?: PedidoFilters): Promise<PedidosResponse>;
/**
 * Get order detail by ID
 * GET /api/v1/pedidos/{id}
 */
export declare function getPedidoDetail(id: number): Promise<Pedido>;
/**
 * Transition order to a new state
 * PATCH /api/v1/pedidos/{id}/estado
 */
export declare function transicionarEstado(pedidoId: number, data: TransicionRequest): Promise<TransicionResponse>;
/**
 * Cancel an order (convenience endpoint)
 * DELETE /api/v1/pedidos/{id}?motivo=...
 *
 * CLIENT: can cancel own PENDIENTE orders
 * ADMIN/PEDIDOS: can cancel PENDIENTE or CONFIRMADO orders
 */
export declare function cancelarPedido(pedidoId: number, motivo: string): Promise<TransicionResponse>;
/**
 * Get order state transition history
 * GET /api/v1/pedidos/{id}/historial
 */
export declare function getPedidoHistorial(pedidoId: number): Promise<any>;
//# sourceMappingURL=api.d.ts.map