/**
 * AddToCartButton — reusable button to add a product to the cart
 *
 * Features:
 * - Calls addItem from cartStore
 * - Shows toast feedback on add
 * - If product (with same personalization) already in cart, shows "En carrito (N)" indicator
 * - Prevents adding if quantity is 0 or exceeds max
 */
import React from 'react';
import type { ProductoParaCarrito } from '../types';
interface AddToCartButtonProps {
    producto: ProductoParaCarrito;
    cantidad?: number;
    personalizacion?: number[];
    /** Optional class name override */
    className?: string;
    /** If true, render as a full-width large button (for ProductDetail) */
    large?: boolean;
    /** Called after the product is added */
    onAdded?: () => void;
}
export declare const AddToCartButton: React.FC<AddToCartButtonProps>;
export default AddToCartButton;
//# sourceMappingURL=AddToCartButton.d.ts.map