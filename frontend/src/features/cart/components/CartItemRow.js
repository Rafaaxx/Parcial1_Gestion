import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useCartStore } from '../store';
export const CartItemRow = ({ item }) => {
    const updateQuantity = useCartStore((s) => s.updateQuantity);
    const removeItem = useCartStore((s) => s.removeItem);
    const handleIncrement = () => {
        updateQuantity(item.productoId, item.cantidad + 1, item.personalizacion);
    };
    const handleDecrement = () => {
        if (item.cantidad <= 1) {
            removeItem(item.productoId, item.personalizacion);
        }
        else {
            updateQuantity(item.productoId, item.cantidad - 1, item.personalizacion);
        }
    };
    const handleRemove = () => {
        removeItem(item.productoId, item.personalizacion);
    };
    const lineSubtotal = item.precio * item.cantidad;
    // Find names of excluded ingredients
    const excludedIngredientNames = item.personalizacion
        .map((id) => {
        const ing = item.ingredientes?.find((i) => i.id === id);
        return ing?.nombre;
    })
        .filter(Boolean);
    return (_jsxs("div", { className: "flex gap-3 py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0", children: [_jsx("div", { className: "flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800", children: item.imagenUrl ? (_jsx("img", { src: item.imagenUrl, alt: item.nombre, className: "w-full h-full object-cover", loading: "lazy" })) : (_jsx("div", { className: "w-full h-full flex items-center justify-center text-gray-400", children: _jsx("svg", { className: "w-6 h-6", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" }) }) })) }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsxs("div", { className: "flex items-start justify-between gap-2", children: [_jsx("h4", { className: "text-sm font-medium text-gray-900 dark:text-gray-100 truncate", children: item.nombre }), _jsx("button", { onClick: handleRemove, className: "flex-shrink-0 p-1 text-gray-400 hover:text-red-500 transition-colors", "aria-label": `Eliminar ${item.nombre}`, children: _jsx("svg", { className: "w-4 h-4", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" }) }) })] }), _jsxs("p", { className: "text-xs text-gray-500 dark:text-gray-400 mt-0.5", children: ["$", item.precio.toFixed(2), " c/u"] }), excludedIngredientNames.length > 0 && (_jsxs("p", { className: "text-xs text-amber-600 dark:text-amber-400 mt-0.5", children: ["Sin: ", excludedIngredientNames.join(', ')] })), _jsxs("div", { className: "flex items-center gap-3 mt-2", children: [_jsxs("div", { className: "flex items-center border border-gray-200 dark:border-gray-700 rounded-md", children: [_jsx("button", { onClick: handleDecrement, className: "px-2 py-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors", "aria-label": "Decrementar cantidad", children: _jsx("svg", { className: "w-3.5 h-3.5", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M20 12H4" }) }) }), _jsx("span", { className: "px-3 py-1 text-sm font-medium text-gray-900 dark:text-gray-100 min-w-[2rem] text-center", children: item.cantidad }), _jsx("button", { onClick: handleIncrement, className: "px-2 py-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors", "aria-label": "Incrementar cantidad", children: _jsx("svg", { className: "w-3.5 h-3.5", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M12 4v16m8-8H4" }) }) })] }), _jsxs("span", { className: "text-sm font-semibold text-gray-900 dark:text-gray-100 ml-auto", children: ["$", lineSubtotal.toFixed(2)] })] })] })] }));
};
export default CartItemRow;
//# sourceMappingURL=CartItemRow.js.map