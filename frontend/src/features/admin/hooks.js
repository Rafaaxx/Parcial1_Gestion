/**
 * Custom hooks for Admin module using TanStack Query
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getResumen, getVentas, getProductosTop, getPedidosPorEstado, getUsuarios, updateUsuario, updateUsuarioEstado, } from './api';
// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════
export const adminKeys = {
    all: ['admin'],
    metrics: () => [...adminKeys.all, 'metrics'],
    resumen: (desde, hasta) => [...adminKeys.metrics(), 'resumen', { desde, hasta }],
    ventas: (granularidad, desde, hasta) => [...adminKeys.metrics(), 'ventas', { granularidad, desde, hasta }],
    productosTop: (top, desde, hasta) => [...adminKeys.metrics(), 'productos-top', { top, desde, hasta }],
    pedidosPorEstado: (desde, hasta) => [...adminKeys.metrics(), 'pedidos-estado', { desde, hasta }],
    usuarios: () => [...adminKeys.all, 'usuarios'],
    usuariosList: (params) => [...adminKeys.usuarios(), 'list', params],
};
// ═══════════════════════════════════════════════════════════════════════════
// Metrics Hooks
// ═══════════════════════════════════════════════════════════════════════════
/**
 * Get dashboard summary metrics
 */
export function useResumen(desde, hasta) {
    return useQuery({
        queryKey: adminKeys.resumen(desde, hasta),
        queryFn: () => getResumen(desde, hasta),
    });
}
/**
 * Get sales by time period
 */
export function useVentas(granularidad = 'dia', desde, hasta) {
    return useQuery({
        queryKey: adminKeys.ventas(granularidad, desde, hasta),
        queryFn: () => getVentas(granularidad, desde, hasta),
    });
}
/**
 * Get top selling products
 */
export function useProductosTop(top = 10, desde, hasta) {
    return useQuery({
        queryKey: adminKeys.productosTop(top, desde, hasta),
        queryFn: () => getProductosTop(top, desde, hasta),
    });
}
/**
 * Get orders grouped by state
 */
export function usePedidosPorEstado(desde, hasta) {
    return useQuery({
        queryKey: adminKeys.pedidosPorEstado(desde, hasta),
        queryFn: () => getPedidosPorEstado(desde, hasta),
    });
}
// ═══════════════════════════════════════════════════════════════════════════
// User Management Hooks
// ═══════════════════════════════════════════════════════════════════════════
/**
 * List users with pagination and filters
 */
export function useUsuarios(skip = 0, limit = 20, busqueda, rol, activo) {
    return useQuery({
        queryKey: adminKeys.usuariosList({ skip, limit, busqueda, rol, activo }),
        queryFn: () => getUsuarios(skip, limit, busqueda, rol, activo),
    });
}
/**
 * Update user data (name, email, roles)
 */
export function useUpdateUsuario() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ usuarioId, data, }) => updateUsuario(usuarioId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: adminKeys.usuarios() });
        },
    });
}
/**
 * Activate or deactivate a user
 */
export function useUpdateUsuarioEstado() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ usuarioId, data, }) => updateUsuarioEstado(usuarioId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: adminKeys.usuarios() });
        },
    });
}
//# sourceMappingURL=hooks.js.map