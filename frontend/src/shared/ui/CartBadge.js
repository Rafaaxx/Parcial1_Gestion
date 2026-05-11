import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
import { useCartStore } from '@/features/cart/store';
export const CartBadge = () => {
    const { user, hasRole } = useAuth();
    const count = useCartStore((state) => state.totalItems());
    // Only visible for CLIENT role or any authenticated user
    if (!user || !hasRole('CLIENT'))
        return null;
    return (_jsxs(Link, { to: "/carrito", className: "relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors", "aria-label": `Carrito de compras${count > 0 ? `, ${count} artículos` : ''}`, children: [_jsx("svg", { className: "w-6 h-6 text-gray-700 dark:text-gray-300", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" }) }), count > 0 && (_jsx("span", { className: "absolute -top-1 -right-1 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full", children: count > 99 ? '99+' : count }))] }));
};
export default CartBadge;
//# sourceMappingURL=CartBadge.js.map