/**
 * CartItemRow — individual item row in the cart drawer
 *
 * Shows:
 * - Product thumbnail
 * - Name, unit price, quantity with +/- controls, line subtotal
 * - Delete/remove button
 * - Excluded ingredients (if personalization exists)
 */
import React from 'react';
import type { CartItem } from '../types';
interface CartItemRowProps {
    item: CartItem;
}
export declare const CartItemRow: React.FC<CartItemRowProps>;
export default CartItemRow;
//# sourceMappingURL=CartItemRow.d.ts.map