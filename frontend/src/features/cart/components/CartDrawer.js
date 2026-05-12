import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
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
import { useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useCartStore } from '../store';
import { CartItemRow } from './CartItemRow';
import { CartSummary } from './CartSummary';
export const CartDrawer = ({ isOpen, onClose }) => {
    const items = useCartStore((s) => s.items);
    const totalItems = useCartStore((s) => s.totalItems());
    // Close on Escape key
    const handleKeyDown = useCallback((e) => {
        if (e.key === 'Escape')
            onClose();
    }, [onClose]);
    useEffect(() => {
        if (isOpen) {
            document.addEventListener('keydown', handleKeyDown);
            // Prevent body scroll when drawer is open
            document.body.style.overflow = 'hidden';
        }
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.body.style.overflow = '';
        };
    }, [isOpen, handleKeyDown]);
    return (_jsxs(_Fragment, { children: [isOpen && (_jsx("div", { className: "fixed inset-0 bg-black/40 z-50 transition-opacity", onClick: onClose, "aria-hidden": "true" })), _jsxs("div", { className: `fixed top-0 right-0 h-full w-full sm:w-[420px] bg-white dark:bg-gray-900 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : 'translate-x-full'}`, role: "dialog", "aria-modal": "true", "aria-label": "Carrito de compras", children: [_jsxs("div", { className: "flex items-center justify-between px-4 py-4 border-b border-gray-200 dark:border-gray-800", children: [_jsxs("h2", { className: "text-lg font-semibold text-gray-900 dark:text-gray-100", children: ["Tu Carrito", totalItems > 0 && (_jsxs("span", { className: "ml-2 text-sm font-normal text-gray-500 dark:text-gray-400", children: ["(", totalItems, " ", totalItems === 1 ? 'artículo' : 'artículos', ")"] }))] }), _jsx("button", { onClick: onClose, className: "p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 hover:text-gray-700 dark:hover:text-gray-300", "aria-label": "Cerrar carrito", children: _jsx("svg", { className: "w-5 h-5", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M6 18L18 6M6 6l12 12" }) }) })] }), _jsxs("div", { className: "flex flex-col h-[calc(100%-64px)]", children: [_jsx("div", { className: "flex-1 overflow-y-auto px-4 py-2", children: items.length === 0 ? (_jsxs("div", { className: "flex flex-col items-center justify-center h-full text-center py-12", children: [_jsx("svg", { className: "w-16 h-16 text-gray-300 dark:text-gray-600 mb-4", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 1.5, d: "M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" }) }), _jsx("p", { className: "text-gray-500 dark:text-gray-400 font-medium mb-2", children: "Tu carrito est\u00E1 vac\u00EDo" }), _jsx("p", { className: "text-sm text-gray-400 dark:text-gray-500 mb-4", children: "Agreg\u00E1 productos del cat\u00E1logo para empezar" }), _jsx(Link, { to: "/productos", onClick: onClose, className: "inline-flex px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors", children: "Ver cat\u00E1logo" })] })) : (items.map((item) => (_jsx(CartItemRow, { item: item }, `${item.productoId}-${JSON.stringify(item.personalizacion)}`)))) }), items.length > 0 && (_jsx("div", { className: "px-4 py-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50", children: _jsx(CartSummary, {}) }))] })] })] }));
};
export default CartDrawer;
//# sourceMappingURL=CartDrawer.js.map