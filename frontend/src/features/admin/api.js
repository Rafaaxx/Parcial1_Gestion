/**
 * API integration for Admin module
 * Handles all HTTP calls to the backend admin endpoints
 */
import { apiClient } from '@/shared/http/client';
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';
/**
 * Helper to get auth token from localStorage (bypass Zustand hydration issues)
 */
const getAuthHeaders = () => {
    try {
        const stored = localStorage.getItem('food-store-auth');
        if (stored) {
            const parsed = JSON.parse(stored);
            const token = parsed.state?.token;
            if (token) {
                return { Authorization: `Bearer ${token}` };
            }
        }
    }
    catch {
        // ignore
    }
    return {};
};
// ═══════════════════════════════════════════════════════════════════════════
// Dashboard Metrics
// ═══════════════════════════════════════════════════════════════════════════
/**
 * Get dashboard metrics summary
 * GET /api/v1/admin/metricas/resumen
 */
export async function getResumen(desde, hasta) {
    const params = {};
    if (desde)
        params.desde = desde;
    if (hasta)
        params.hasta = hasta;
    const response = await apiClient.get(`${API_BASE}${API_VERSION}/admin/metricas/resumen`, { params, headers: getAuthHeaders() });
    return response.data;
}
/**
 * Get sales by period
 * GET /api/v1/admin/metricas/ventas
 */
export async function getVentas(granularidad = 'dia', desde, hasta) {
    const params = { granularidad };
    if (desde)
        params.desde = desde;
    if (hasta)
        params.hasta = hasta;
    const response = await apiClient.get(`${API_BASE}${API_VERSION}/admin/metricas/ventas`, { params, headers: getAuthHeaders() });
    return response.data;
}
/**
 * Get top selling products
 * GET /api/v1/admin/metricas/productos-top
 */
export async function getProductosTop(top = 10, desde, hasta) {
    const params = { top };
    if (desde)
        params.desde = desde;
    if (hasta)
        params.hasta = hasta;
    const response = await apiClient.get(`${API_BASE}${API_VERSION}/admin/metricas/productos-top`, { params, headers: getAuthHeaders() });
    return response.data;
}
/**
 * Get orders by state
 * GET /api/v1/admin/metricas/pedidos-por-estado
 */
export async function getPedidosPorEstado(desde, hasta) {
    const params = {};
    if (desde)
        params.desde = desde;
    if (hasta)
        params.hasta = hasta;
    const response = await apiClient.get(`${API_BASE}${API_VERSION}/admin/metricas/pedidos-por-estado`, { params, headers: getAuthHeaders() });
    return response.data;
}
// ═══════════════════════════════════════════════════════════════════════════
// User Management
// ═══════════════════════════════════════════════════════════════════════════
/**
 * List users with pagination, search, and filters
 * GET /api/v1/admin/usuarios
 */
export async function getUsuarios(skip = 0, limit = 20, busqueda, rol, activo) {
    const params = { skip, limit };
    if (busqueda)
        params.busqueda = busqueda;
    if (rol)
        params.rol = rol;
    if (activo !== undefined)
        params.activo = activo;
    const response = await apiClient.get(`${API_BASE}${API_VERSION}/admin/usuarios`, { params, headers: getAuthHeaders() });
    return response.data;
}
/**
 * Update user data (name, email, roles)
 * PUT /api/v1/admin/usuarios/{id}
 */
export async function updateUsuario(usuarioId, data) {
    const response = await apiClient.put(`${API_BASE}${API_VERSION}/admin/usuarios/${usuarioId}`, data, { headers: getAuthHeaders() });
    return response.data;
}
/**
 * Activate or deactivate a user
 * PATCH /api/v1/admin/usuarios/{id}/estado
 */
export async function updateUsuarioEstado(usuarioId, data) {
    const response = await apiClient.patch(`${API_BASE}${API_VERSION}/admin/usuarios/${usuarioId}/estado`, data, { headers: getAuthHeaders() });
    return response.data;
}
//# sourceMappingURL=api.js.map