/**
 * Custom hooks for Pedidos (Orders) module
 */
import { TransicionRequest, PedidoFilters } from '../types';
export declare const pedidoKeys: {
    all: readonly ["pedidos"];
    lists: () => readonly ["pedidos", "list"];
    list: (params: {
        skip?: number;
        limit?: number;
        filtros?: PedidoFilters;
    }) => readonly ["pedidos", "list", {
        skip?: number;
        limit?: number;
        filtros?: PedidoFilters;
    }];
    details: () => readonly ["pedidos", "detail"];
    detail: (id: number) => readonly ["pedidos", "detail", number];
};
/**
 * Hook to fetch list of orders with optional filters
 */
export declare function usePedidos(skip?: number, limit?: number, filtros?: PedidoFilters): import("@tanstack/react-query").UseQueryResult<import("../types").PedidosResponse, Error>;
/**
 * Hook to fetch order detail
 */
export declare function usePedidoDetail(pedidoId: number): import("@tanstack/react-query").UseQueryResult<import("../types").Pedido, Error>;
/**
 * Hook to transition order state
 */
export declare function useTransicionEstado(): import("@tanstack/react-query").UseMutationResult<import("../types").TransicionResponse, Error, {
    pedidoId: number;
    data: TransicionRequest;
}, unknown>;
/**
 * Hook to cancel an order
 */
export declare function useCancelarPedido(): import("@tanstack/react-query").UseMutationResult<import("../types").TransicionResponse, Error, {
    pedidoId: number;
    motivo: string;
}, unknown>;
/**
 * Helper hook to get available transitions based on current state and user role
 */
import { TransicionAction } from '../types';
export declare function getTransicionesDisponibles(estadoActual: string, userRoles: string[]): TransicionAction[];
//# sourceMappingURL=index.d.ts.map