/**
 * API integration for Pedidos (Orders)
 * Handles all HTTP calls to the backend orders endpoints
 */
import axios from 'axios';
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';
/**
 * Get list of orders with pagination and optional filters
 * GET /api/v1/pedidos
 *
 * CLIENT role: returns only own orders
 * ADMIN/PEDIDOS roles: returns all orders
 */
export async function getPedidos(skip = 0, limit = 20, filtros) {
    try {
        const params = { skip, limit };
        // Add filters if provided
        if (filtros) {
            if (filtros.estado)
                params.estado = filtros.estado;
            if (filtros.desde)
                params.desde = filtros.desde;
            if (filtros.hasta)
                params.hasta = filtros.hasta;
            if (filtros.busqueda)
                params.busqueda = filtros.busqueda;
        }
        const response = await axios.get(`${API_BASE}${API_VERSION}/pedidos`, { params });
        return response.data;
    }
    catch (error) {
        if (axios.isAxiosError(error)) {
            const status = error.response?.status;
            const message = error.response?.data?.detail || error.message;
            if (status === 403) {
                throw new Error('No tienes permisos para ver pedidos');
            }
            if (status === 500) {
                throw new Error('Error del servidor al obtener pedidos');
            }
            throw new Error(message || 'Error al obtener pedidos');
        }
        throw error;
    }
}
/**
 * Get order detail by ID
 * GET /api/v1/pedidos/{id}
 */
export async function getPedidoDetail(id) {
    try {
        const response = await axios.get(`${API_BASE}${API_VERSION}/pedidos/${id}`);
        return response.data;
    }
    catch (error) {
        if (axios.isAxiosError(error)) {
            const status = error.response?.status;
            if (status === 404) {
                throw new Error('Pedido no encontrado');
            }
            if (status === 403) {
                throw new Error('No tienes permisos para ver este pedido');
            }
            if (status === 500) {
                throw new Error('Error del servidor al obtener el pedido');
            }
            throw new Error(error.response?.data?.detail || error.message || 'Error al obtener pedido');
        }
        throw error;
    }
}
/**
 * Transition order to a new state
 * PATCH /api/v1/pedidos/{id}/estado
 */
export async function transicionarEstado(pedidoId, data) {
    try {
        const response = await axios.patch(`${API_BASE}${API_VERSION}/pedidos/${pedidoId}/estado`, data);
        return response.data;
    }
    catch (error) {
        if (axios.isAxiosError(error)) {
            const status = error.response?.status;
            const message = error.response?.data?.detail || error.message;
            if (status === 404) {
                throw new Error('Pedido no encontrado');
            }
            if (status === 422) {
                throw new Error(message || 'Transición no válida');
            }
            if (status === 403) {
                throw new Error('No tienes permisos para esta transición');
            }
            if (status === 500) {
                throw new Error('Error del servidor al cambiar estado');
            }
            throw new Error(message || 'Error al cambiar estado del pedido');
        }
        throw error;
    }
}
/**
 * Cancel an order (convenience endpoint)
 * DELETE /api/v1/pedidos/{id}?motivo=...
 *
 * CLIENT: can cancel own PENDIENTE orders
 * ADMIN/PEDIDOS: can cancel PENDIENTE or CONFIRMADO orders
 */
export async function cancelarPedido(pedidoId, motivo) {
    try {
        const response = await axios.delete(`${API_BASE}${API_VERSION}/pedidos/${pedidoId}`, { params: { motivo } });
        return response.data;
    }
    catch (error) {
        if (axios.isAxiosError(error)) {
            const status = error.response?.status;
            const message = error.response?.data?.detail || error.message;
            if (status === 404) {
                throw new Error('Pedido no encontrado');
            }
            if (status === 422) {
                throw new Error(message || 'No se puede cancelar el pedido');
            }
            if (status === 403) {
                throw new Error('No tienes permisos para cancelar este pedido');
            }
            if (status === 500) {
                throw new Error('Error del servidor al cancelar pedido');
            }
            throw new Error(message || 'Error al cancelar pedido');
        }
        throw error;
    }
}
/**
 * Get order state transition history
 * GET /api/v1/pedidos/{id}/historial
 */
export async function getPedidoHistorial(pedidoId) {
    try {
        const response = await axios.get(`${API_BASE}${API_VERSION}/pedidos/${pedidoId}/historial`);
        return response.data;
    }
    catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Error al obtener historial');
        }
        throw error;
    }
}
//# sourceMappingURL=api.js.map