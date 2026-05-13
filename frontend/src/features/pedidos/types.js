/**
 * Types for Pedido (Order) module
 */
export const ESTADOS_TERMINALES = ['ENTREGADO', 'CANCELADO'];
export function esEstadoTerminal(estado) {
    return ESTADOS_TERMINALES.includes(estado);
}
export const ESTADO_LABELS = {
    PENDIENTE: 'Pendiente',
    CONFIRMADO: 'Confirmado',
    EN_PREP: 'En Preparación',
    EN_CAMINO: 'En Camino',
    ENTREGADO: 'Entregado',
    CANCELADO: 'Cancelado',
};
export const ESTADO_COLORS = {
    PENDIENTE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    CONFIRMADO: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    EN_PREP: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    EN_CAMINO: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    ENTREGADO: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    CANCELADO: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
};
//# sourceMappingURL=types.js.map