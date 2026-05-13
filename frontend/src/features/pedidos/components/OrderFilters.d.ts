/**
 * OrderFilters - Filtros para el listado de pedidos
 */
import React from 'react';
import { PedidoFilters } from '../types';
interface OrderFiltersProps {
    filtros: PedidoFilters;
    onChange: (filtros: PedidoFilters) => void;
}
export declare const OrderFilters: React.FC<OrderFiltersProps>;
export default OrderFilters;
//# sourceMappingURL=OrderFilters.d.ts.map