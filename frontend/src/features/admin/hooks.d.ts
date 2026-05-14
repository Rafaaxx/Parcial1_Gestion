/**
 * Custom hooks for Admin module using TanStack Query
 */
import type { UpdateUsuarioRequest, UpdateUsuarioEstadoRequest } from './types';
export declare const adminKeys: {
    all: readonly ["admin"];
    metrics: () => readonly ["admin", "metrics"];
    resumen: (desde?: string, hasta?: string) => readonly ["admin", "metrics", "resumen", {
        readonly desde: string | undefined;
        readonly hasta: string | undefined;
    }];
    ventas: (granularidad: string, desde?: string, hasta?: string) => readonly ["admin", "metrics", "ventas", {
        readonly granularidad: string;
        readonly desde: string | undefined;
        readonly hasta: string | undefined;
    }];
    productosTop: (top: number, desde?: string, hasta?: string) => readonly ["admin", "metrics", "productos-top", {
        readonly top: number;
        readonly desde: string | undefined;
        readonly hasta: string | undefined;
    }];
    pedidosPorEstado: (desde?: string, hasta?: string) => readonly ["admin", "metrics", "pedidos-estado", {
        readonly desde: string | undefined;
        readonly hasta: string | undefined;
    }];
    usuarios: () => readonly ["admin", "usuarios"];
    usuariosList: (params: Record<string, unknown>) => readonly ["admin", "usuarios", "list", Record<string, unknown>];
};
/**
 * Get dashboard summary metrics
 */
export declare function useResumen(desde?: string, hasta?: string): import("@tanstack/react-query").UseQueryResult<import("./types").ResumenMetricas, Error>;
/**
 * Get sales by time period
 */
export declare function useVentas(granularidad?: 'dia' | 'semana' | 'mes', desde?: string, hasta?: string): import("@tanstack/react-query").UseQueryResult<import("./types").VentaPeriodo[], Error>;
/**
 * Get top selling products
 */
export declare function useProductosTop(top?: number, desde?: string, hasta?: string): import("@tanstack/react-query").UseQueryResult<import("./types").ProductoTop[], Error>;
/**
 * Get orders grouped by state
 */
export declare function usePedidosPorEstado(desde?: string, hasta?: string): import("@tanstack/react-query").UseQueryResult<import("./types").PedidoEstadoItem[], Error>;
/**
 * List users with pagination and filters
 */
export declare function useUsuarios(skip?: number, limit?: number, busqueda?: string, rol?: string, activo?: boolean): import("@tanstack/react-query").UseQueryResult<import("./types").UsuarioAdminListResponse, Error>;
/**
 * Update user data (name, email, roles)
 */
export declare function useUpdateUsuario(): import("@tanstack/react-query").UseMutationResult<import("./types").UsuarioAdmin, Error, {
    usuarioId: number;
    data: UpdateUsuarioRequest;
}, unknown>;
/**
 * Activate or deactivate a user
 */
export declare function useUpdateUsuarioEstado(): import("@tanstack/react-query").UseMutationResult<import("./types").UsuarioAdmin, Error, {
    usuarioId: number;
    data: UpdateUsuarioEstadoRequest;
}, unknown>;
//# sourceMappingURL=hooks.d.ts.map