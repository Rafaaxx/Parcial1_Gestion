/**
 * CartDrawer — slide-over panel from the right side
 *
 * Features:
 * - Dark overlay behind drawer (click to close)
 * - Close (X) button
 * - Renders list of CartItemRow components
 * - Empty state: "Tu carrito está vacío" + link to catalog
 * - Summary section with totals
 */
import React from 'react';
interface CartDrawerProps {
    isOpen: boolean;
    onClose: () => void;
}
export declare const CartDrawer: React.FC<CartDrawerProps>;
export default CartDrawer;
//# sourceMappingURL=CartDrawer.d.ts.map