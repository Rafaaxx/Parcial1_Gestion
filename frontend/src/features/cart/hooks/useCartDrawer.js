/**
 * useCartDrawer — custom hook to manage cart drawer open/close state
 */
import { useState, useCallback, useMemo } from 'react';
export function useCartDrawer() {
    const [isOpen, setIsOpen] = useState(false);
    const openCart = useCallback(() => setIsOpen(true), []);
    const closeCart = useCallback(() => setIsOpen(false), []);
    const toggleCart = useCallback(() => setIsOpen((prev) => !prev), []);
    return useMemo(() => ({ isOpen, openCart, closeCart, toggleCart }), [isOpen, openCart, closeCart, toggleCart]);
}
export default useCartDrawer;
//# sourceMappingURL=useCartDrawer.js.map