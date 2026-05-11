import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Root App component with providers, theme support, and routing
 */
import { useEffect, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { useTheme } from '@/shared/hooks';
import { ProtectedRoute } from '@/shared/routing';
import { Layout } from '@/shared/components/Navigation';
import { Skeleton } from '@/shared/ui';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { UnauthorizedPage } from '@/pages/UnauthorizedPage';
import { AdminDashboardPage } from '@/pages/admin/DashboardPage';
import { IngredientsAdminPage } from '@/pages/admin/IngredientsPage';
// Create QueryClient for React Query
const queryClient = new QueryClient();
const HomePage = () => (_jsx("div", { className: "min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-50", children: _jsxs("div", { className: "container mx-auto px-4 py-8", children: [_jsx("h1", { className: "text-4xl font-bold mb-8", children: "Food Store - Welcome \u2705" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-gradient-to-br from-sky-50 to-sky-100 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 border border-sky-200 dark:border-gray-700", children: [_jsx("h2", { className: "text-2xl font-semibold mb-3", children: "Welcome to Food Store" }), _jsx("p", { className: "text-gray-700 dark:text-gray-300 mb-4", children: "Frontend is now ready with routing, layout, and role-based access control." }), _jsxs("div", { className: "flex gap-2 flex-wrap", children: [_jsx("span", { className: "px-3 py-1 bg-sky-500 text-white rounded-full text-sm", children: "React 19" }), _jsx("span", { className: "px-3 py-1 bg-sky-500 text-white rounded-full text-sm", children: "React Router v6" }), _jsx("span", { className: "px-3 py-1 bg-sky-500 text-white rounded-full text-sm", children: "React Query" })] })] }), _jsxs("div", { className: "bg-gradient-to-br from-green-50 to-green-100 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 border border-green-200 dark:border-gray-700", children: [_jsx("h2", { className: "text-2xl font-semibold mb-3", children: "Next Steps" }), _jsxs("ul", { className: "space-y-2 text-gray-700 dark:text-gray-300 text-sm", children: [_jsx("li", { children: "\u2713 Auth store with role-based access" }), _jsx("li", { children: "\u2713 Protected routes with RBAC" }), _jsx("li", { children: "\u2713 Admin layout with sidebar" }), _jsx("li", { children: "\u2713 Ingredientes page (CHANGE-04)" }), _jsx("li", { children: "\u2192 Login/Register flow (CHANGE-01)" })] })] })] })] }) }));
const PageSkeleton = () => (_jsxs("div", { className: "p-8", children: [_jsx(Skeleton, { className: "h-10 w-1/3 mb-6" }), _jsxs("div", { className: "space-y-4", children: [_jsx(Skeleton, { className: "h-6 w-full" }), _jsx(Skeleton, { className: "h-6 w-full" }), _jsx(Skeleton, { className: "h-6 w-2/3" })] })] }));
const PlaceholderPage = ({ title }) => (_jsxs("div", { className: "p-8", children: [_jsx("h1", { className: "text-4xl font-bold mb-4 text-gray-900 dark:text-white", children: title }), _jsx("p", { className: "text-gray-600 dark:text-gray-400", children: "Coming soon..." })] }));
export const App = () => {
    const { theme, applyTheme } = useTheme();
    // Apply theme on mount and when it changes
    useEffect(() => {
        applyTheme(theme);
    }, [theme, applyTheme]);
    return (_jsx("div", { className: `min-h-screen ${theme === 'dark' ? 'dark' : ''}`, children: _jsx(QueryClientProvider, { client: queryClient, children: _jsx(Router, { children: _jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(HomePage, {}) }), _jsx(Route, { path: "/unauthorized", element: _jsx(UnauthorizedPage, {}) }), _jsxs(Route, { path: "/app", element: _jsx(ProtectedRoute, { requiredRoles: ['ADMIN', 'STOCK', 'PEDIDOS', 'CLIENT'], children: _jsx(Layout, {}) }), children: [_jsx(Route, { path: "dashboard", element: _jsx(ProtectedRoute, { requiredRoles: ['ADMIN', 'STOCK', 'PEDIDOS'], children: _jsx(AdminDashboardPage, {}) }) }), _jsx(Route, { path: "ingredients", element: _jsx(ProtectedRoute, { requiredRoles: ['STOCK', 'ADMIN'], children: _jsx(Suspense, { fallback: _jsx(PageSkeleton, {}), children: _jsx(IngredientsAdminPage, {}) }) }) }), _jsx(Route, { path: "catalog", element: _jsx(PlaceholderPage, { title: "Cat\u00E1logo" }) }), _jsx(Route, { path: "cart", element: _jsx(PlaceholderPage, { title: "Carrito" }) }), _jsx(Route, { path: "orders", element: _jsx(PlaceholderPage, { title: "Mis Pedidos" }) }), _jsx(Route, { path: "profile", element: _jsx(PlaceholderPage, { title: "Mi Perfil" }) }), _jsx(Route, { path: "products", element: _jsx(PlaceholderPage, { title: "Productos" }) }), _jsx(Route, { path: "categories", element: _jsx(PlaceholderPage, { title: "Categor\u00EDas" }) }), _jsx(Route, { path: "stock", element: _jsx(PlaceholderPage, { title: "Stock" }) }), _jsx(Route, { path: "orders-panel", element: _jsx(PlaceholderPage, { title: "Panel de Pedidos" }) }), _jsx(Route, { path: "users", element: _jsx(PlaceholderPage, { title: "Usuarios" }) }), _jsx(Route, { path: "metrics", element: _jsx(PlaceholderPage, { title: "M\u00E9tricas" }) }), _jsx(Route, { path: "settings", element: _jsx(PlaceholderPage, { title: "Configuraci\u00F3n" }) })] }), _jsx(Route, { path: "*", element: _jsx(NotFoundPage, {}) })] }) }) }) }));
};
//# sourceMappingURL=App.js.map