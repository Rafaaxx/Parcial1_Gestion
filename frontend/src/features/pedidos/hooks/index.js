/**
 * Custom hooks for Pedidos (Orders) module
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getPedidos, getPedidoDetail, transicionarEstado, cancelarPedido, } from '../api';
// Query keys
export const pedidoKeys = {
    all: ['pedidos'],
    lists: () => [...pedidoKeys.all, 'list'],
    list: (params) => [...pedidoKeys.lists(), params],
    details: () => [...pedidoKeys.all, 'detail'],
    detail: (id) => [...pedidoKeys.details(), id],
};
/**
 * Hook to fetch list of orders with optional filters
 */
export function usePedidos(skip = 0, limit = 20, filtros) {
    return useQuery({
        queryKey: pedidoKeys.list({ skip, limit, filtros }),
        queryFn: () => getPedidos(skip, limit, filtros),
    });
}
/**
 * Hook to fetch order detail
 */
export function usePedidoDetail(pedidoId) {
    return useQuery({
        queryKey: pedidoKeys.detail(pedidoId),
        queryFn: () => getPedidoDetail(pedidoId),
        enabled: pedidoId > 0,
    });
}
/**
 * Hook to transition order state
 */
export function useTransicionEstado() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ pedidoId, data }) => transicionarEstado(pedidoId, data),
        onSuccess: () => {
            // Invalidate pedidos list and detail queries
            queryClient.invalidateQueries({ queryKey: pedidoKeys.lists() });
            queryClient.invalidateQueries({ queryKey: pedidoKeys.all });
        },
    });
}
/**
 * Hook to cancel an order
 */
export function useCancelarPedido() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ pedidoId, motivo }) => cancelarPedido(pedidoId, motivo),
        onSuccess: () => {
            // Invalidate pedidos list and detail queries
            queryClient.invalidateQueries({ queryKey: pedidoKeys.lists() });
            queryClient.invalidateQueries({ queryKey: pedidoKeys.all });
        },
    });
}
const TRANSICIONES_POR_ESTADO = {
    PENDIENTE: [
        {
            label: 'Confirmar',
            nuevo_estado: 'CONFIRMADO',
            allowed_roles: ['ADMIN', 'PEDIDOS'],
            icon: '✓',
        },
        {
            label: 'Cancelar',
            nuevo_estado: 'CANCELADO',
            requires_motivo: true,
            allowed_roles: ['ADMIN', 'PEDIDOS'],
            icon: '✕',
        },
    ],
    CONFIRMADO: [
        {
            label: 'En Preparación',
            nuevo_estado: 'EN_PREP',
            allowed_roles: ['ADMIN', 'PEDIDOS'],
            icon: '🍕',
        },
        {
            label: 'Cancelar',
            nuevo_estado: 'CANCELADO',
            requires_motivo: true,
            allowed_roles: ['ADMIN', 'PEDIDOS'],
            icon: '✕',
        },
    ],
    EN_PREP: [
        {
            label: 'En Camino',
            nuevo_estado: 'EN_CAMINO',
            allowed_roles: ['ADMIN', 'PEDIDOS'],
            icon: '🚚',
        },
        {
            label: 'Cancelar',
            nuevo_estado: 'CANCELADO',
            requires_motivo: true,
            allowed_roles: ['ADMIN', 'PEDIDOS'],
            icon: '✕',
        },
    ],
    EN_CAMINO: [
        {
            label: 'Entregado',
            nuevo_estado: 'ENTREGADO',
            allowed_roles: ['ADMIN', 'PEDIDOS'],
            icon: '✅',
        },
    ],
    ENTREGADO: [],
    CANCELADO: [],
};
export function getTransicionesDisponibles(estadoActual, userRoles) {
    const transiciones = TRANSICIONES_POR_ESTADO[estadoActual] || [];
    return transiciones.filter((t) => t.allowed_roles.some((role) => userRoles.includes(role)));
}
//# sourceMappingURL=index.js.map