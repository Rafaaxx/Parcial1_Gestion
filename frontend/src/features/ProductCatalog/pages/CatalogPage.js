import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * CatalogPage Component
 * Main catalog page with filters sidebar, product grid, and pagination
 * Layout: Responsive - sidebar on desktop, top bar on mobile
 */
import { useNavigate } from 'react-router-dom';
import { CatalogFilters } from '../components/CatalogFilters';
import { ProductList } from '../components/ProductList';
import { PaginationControls } from '../components/PaginationControls';
import { useProducts } from '../hooks/useCatalogFilters';
import { useCatalogStore } from '../stores/catalogStore';
export function CatalogPage() {
    const navigate = useNavigate();
    const { products, total, isLoading, error } = useProducts();
    const { currentPage, limit, setPage } = useCatalogStore();
    const handleProductClick = (id) => {
        navigate(`/catalog/${id}`);
    };
    const handlePageChange = (page) => {
        setPage(page);
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    return (_jsx("div", { className: "min-h-screen bg-gray-50 py-8", children: _jsxs("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8", children: [_jsxs("div", { className: "mb-8", children: [_jsx("h1", { className: "text-4xl font-bold text-gray-900 mb-2", children: "Public Catalog" }), _jsxs("p", { className: "text-gray-600", children: ["Browse our selection of ", total, " available products"] })] }), _jsxs("div", { className: "flex flex-col lg:flex-row gap-8", children: [_jsx("div", { className: "w-full lg:w-64 flex-shrink-0", children: _jsx(CatalogFilters, {}) }), _jsxs("div", { className: "flex-1 min-w-0", children: [error && (_jsx("div", { className: "mb-6 p-4 bg-red-50 border border-red-200 rounded-lg", children: _jsx("p", { className: "text-red-800 font-medium", children: error instanceof Error ? error.message : 'Failed to load products' }) })), _jsx(ProductList, { products: products, onProductClick: handleProductClick, isLoading: isLoading }), !isLoading && products.length > 0 && (_jsx(PaginationControls, { currentPage: currentPage, totalItems: total, itemsPerPage: limit, onPageChange: handlePageChange, isLoading: isLoading })), !isLoading && !error && products.length === 0 && (_jsxs("div", { className: "text-center py-12", children: [_jsx("p", { className: "text-gray-600 mb-4", children: "No products match your filters." }), _jsx("button", { onClick: () => window.location.reload(), className: "px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors", children: "Try Again" })] }))] })] })] }) }));
}
//# sourceMappingURL=CatalogPage.js.map