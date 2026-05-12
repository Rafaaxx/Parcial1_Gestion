import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useCartStore } from '../store';
export const CartSummary = ({ hideCheckoutButton = false }) => {
    const subtotal = useCartStore((s) => s.subtotal());
    const costoEnvio = useCartStore((s) => s.costoEnvio());
    const total = useCartStore((s) => s.total());
    const items = useCartStore((s) => s.items);
    if (items.length === 0)
        return null;
    return (_jsxs("div", { className: "border-t border-gray-200 dark:border-gray-700 pt-4 space-y-3", children: [_jsxs("div", { className: "flex justify-between text-sm", children: [_jsx("span", { className: "text-gray-600 dark:text-gray-400", children: "Subtotal" }), _jsxs("span", { className: "text-gray-900 dark:text-gray-100 font-medium", children: ["$", subtotal.toFixed(2)] })] }), _jsxs("div", { className: "flex justify-between text-sm", children: [_jsx("span", { className: "text-gray-600 dark:text-gray-400", children: "Env\u00EDo" }), _jsxs("span", { className: "text-gray-900 dark:text-gray-100 font-medium", children: ["$", costoEnvio.toFixed(2)] })] }), _jsx("hr", { className: "border-gray-200 dark:border-gray-700" }), _jsxs("div", { className: "flex justify-between text-base", children: [_jsx("span", { className: "text-gray-900 dark:text-gray-100 font-semibold", children: "Total" }), _jsxs("span", { className: "text-gray-900 dark:text-gray-100 font-bold text-lg", children: ["$", total.toFixed(2)] })] }), !hideCheckoutButton && (_jsxs("div", { className: "relative group pt-2", children: [_jsx("button", { disabled: true, className: "w-full py-3 px-4 bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 font-semibold rounded-lg cursor-not-allowed text-sm", children: "Ir a pagar" }), _jsx("div", { className: "absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block", children: _jsxs("div", { className: "bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded py-1 px-2 whitespace-nowrap shadow-lg", children: ["Pr\u00F3ximamente", _jsx("div", { className: "absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-100" })] }) })] }))] }));
};
export default CartSummary;
//# sourceMappingURL=CartSummary.js.map