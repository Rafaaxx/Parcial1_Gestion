import { jsx as _jsx } from "react/jsx-runtime";
/**
 * AddToCartButton — reusable button to add a product to the cart
 *
 * Features:
 * - Calls addItem from cartStore
 * - Shows toast feedback on add
 * - If product (with same personalization) already in cart, shows "En carrito (N)" indicator
 * - Prevents adding if quantity is 0 or exceeds max
 */
import { useCallback } from 'react';
import { useCartStore } from '../store';
import { useToast } from './ToastNotifier';
import { CART_MAX_ITEMS } from '../types';
export const AddToCartButton = ({ producto, cantidad = 1, personalizacion = [], className = '', large = false, onAdded, }) => {
    const addItem = useCartStore((s) => s.addItem);
    const items = useCartStore((s) => s.items);
    const { showToast } = useToast();
    // Check if this exact product + personalization is already in cart
    const existingItem = items.find((item) => item.productoId === producto.id &&
        JSON.stringify([...item.personalizacion].sort()) === JSON.stringify([...personalizacion].sort()));
    const currentInCart = existingItem?.cantidad ?? 0;
    const isAtMax = currentInCart >= CART_MAX_ITEMS;
    const isDisabled = cantidad <= 0 || isAtMax;
    const handleAdd = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (isDisabled)
            return;
        addItem(producto, cantidad, personalizacion);
        showToast('success', `${producto.nombre} agregado al carrito`);
        onAdded?.();
    }, [addItem, producto, cantidad, personalizacion, isDisabled, showToast, onAdded]);
    const baseClasses = large
        ? 'w-full py-3 px-6 text-base font-semibold rounded-lg'
        : 'px-3 py-2 text-sm font-medium rounded-lg';
    const colorClasses = existingItem
        ? 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400 dark:hover:bg-green-900/50 border border-green-300 dark:border-green-700'
        : 'bg-primary-600 hover:bg-primary-700 text-white dark:bg-primary-500 dark:hover:bg-primary-600';
    const disabledClasses = isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer transition-colors';
    return (_jsx("button", { onClick: handleAdd, disabled: isDisabled, className: `${baseClasses} ${colorClasses} ${disabledClasses} ${className}`, title: isAtMax ? `Máximo ${CART_MAX_ITEMS} unidades` : undefined, children: existingItem ? `En carrito (${currentInCart})` : 'Agregar al carrito' }));
};
export default AddToCartButton;
//# sourceMappingURL=AddToCartButton.js.map