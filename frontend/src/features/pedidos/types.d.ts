/**
 * Types for Pedido (Order) module
 */
export type EstadoPedido = 'PENDIENTE' | 'CONFIRMADO' | 'EN_PREP' | 'EN_CAMINO' | 'ENTREGADO' | 'CANCELADO';
export interface ClienteInfo {
    id: number;
    nombre?: string | null;
    email: string;
}
export interface DetallePedido {
    id: number;
    producto_id: number;
    nombre_snapshot: string;
    precio_snapshot: number;
    cantidad: number;
    personalizacion?: number[] | null;
    created_at: string;
}
export interface HistorialEstado {
    id: number;
    estado_desde: string | null;
    estado_hacia: string;
    observacion?: string | null;
    usuario_id?: number | null;
    created_at: string;
}
export interface Pedido {
    id: number;
    usuario_id: number;
    estado_codigo: string;
    total: number;
    costo_envio: number;
    forma_pago_codigo: string;
    direccion_id?: number | null;
    notas?: string | null;
    detalles: DetallePedido[];
    historial: HistorialEstado[];
    created_at: string;
    updated_at: string;
    cliente?: ClienteInfo | null;
}
export interface PedidoListItem {
    id: number;
    usuario_id: number;
    estado_codigo: string;
    total: number;
    costo_envio: number;
    created_at: string;
    cliente?: ClienteInfo | null;
}
export interface PedidosResponse {
    items: PedidoListItem[];
    total: number;
    skip: number;
    limit: number;
}
export interface PedidoFilters {
    estado?: string;
    desde?: string;
    hasta?: string;
    busqueda?: string;
}
export interface TransicionRequest {
    nuevo_estado: EstadoPedido;
    motivo?: string;
}
export interface TransicionResponse {
    id: number;
    estado_codigo: string;
    mensaje: string;
}
export interface TransicionAction {
    label: string;
    nuevo_estado: EstadoPedido;
    requires_motivo?: boolean;
    allowed_roles: string[];
    icon?: string;
}
export declare const ESTADOS_TERMINALES: EstadoPedido[];
export declare function esEstadoTerminal(estado: string): boolean;
export declare const ESTADO_LABELS: Record<EstadoPedido, string>;
export declare const ESTADO_COLORS: Record<EstadoPedido, string>;
//# sourceMappingURL=types.d.ts.map