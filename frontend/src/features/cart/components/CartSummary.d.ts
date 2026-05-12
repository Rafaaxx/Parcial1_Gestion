/**
 * CartSummary — bottom section of cart drawer
 *
 * Shows:
 * - Subtotal, costo de envío ($50), divider, total
 * - Checkout button: disabled with tooltip "Próximamente" (CHANGE-09 not implemented)
 */
import React from 'react';
interface CartSummaryProps {
    /** Optional override: set to true to hide the checkout button (e.g. in full-page view with its own button) */
    hideCheckoutButton?: boolean;
}
export declare const CartSummary: React.FC<CartSummaryProps>;
export default CartSummary;
//# sourceMappingURL=CartSummary.d.ts.map