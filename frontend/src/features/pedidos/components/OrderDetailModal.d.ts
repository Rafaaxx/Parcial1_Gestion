/**
 * OrderDetailModal - Modal con tabs para ver detalle del pedido
 */
import React from 'react';
import { Pedido } from '../types';
interface OrderDetailModalProps {
    pedido: Pedido | null;
    open: boolean;
    onClose: () => void;
}
export declare const OrderDetailModal: React.FC<OrderDetailModalProps>;
export default OrderDetailModal;
//# sourceMappingURL=OrderDetailModal.d.ts.map