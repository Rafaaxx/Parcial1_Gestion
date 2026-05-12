import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { ProductCard } from './ProductCard';
export function ProductList({ products, onProductClick, isLoading }) {
    if (isLoading) {
        return (_jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6", children: Array.from({ length: 8 }).map((_, i) => (_jsx("div", { className: "bg-gray-200 rounded-lg h-80 animate-pulse" }, i))) }));
    }
    if (!products || products.length === 0) {
        return (_jsxs("div", { className: "flex flex-col items-center justify-center py-12", children: [_jsx("svg", { className: "w-16 h-16 text-gray-400 mb-4", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", "aria-hidden": "true", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 1.5, d: "M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" }) }), _jsx("p", { className: "text-gray-600 text-lg font-medium mb-2", children: "No products found" }), _jsx("p", { className: "text-gray-500 text-sm", children: "Try adjusting your filters or search terms" })] }));
    }
    return (_jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6", children: products.map((product) => (_jsx(ProductCard, { product: product, onClick: () => onProductClick?.(product.id) }, product.id))) }));
}
//# sourceMappingURL=ProductList.js.map