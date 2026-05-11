import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore, userHasRole } from '@/features/auth/store';
const NAV_ITEMS = [
    {
        label: 'Dashboard',
        href: '/admin',
        requiredRoles: ['ADMIN', 'STOCK', 'PEDIDOS'],
        icon: '📊',
    },
    {
        label: 'Ingredientes',
        href: '/admin/ingredientes',
        requiredRoles: ['STOCK', 'ADMIN'],
        icon: '🥬',
    },
    {
        label: 'Categorías',
        href: '/admin/categorias',
        requiredRoles: ['STOCK', 'ADMIN'],
        icon: '🏷️',
    },
    {
        label: 'Productos',
        href: '/admin/productos',
        requiredRoles: ['STOCK', 'ADMIN'],
        icon: '📦',
    },
    {
        label: 'Usuarios',
        href: '/admin/usuarios',
        requiredRoles: ['ADMIN'],
        icon: '👥',
    },
];
export const AdminLayout = ({ children }) => {
    const { user } = useAuthStore();
    const location = useLocation();
    // Filter nav items based on user roles
    const visibleNavItems = NAV_ITEMS.filter((item) => userHasRole(user, item.requiredRoles));
    const isActive = (href) => location.pathname === href;
    return (_jsxs("div", { className: "flex h-screen bg-gray-50 dark:bg-gray-950", children: [_jsx("aside", { className: "w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 shadow-sm", children: _jsxs("div", { className: "h-full flex flex-col", children: [_jsxs("div", { className: "p-6 border-b border-gray-200 dark:border-gray-800", children: [_jsx("h1", { className: "text-xl font-bold text-gray-900 dark:text-white", children: "Food Store" }), _jsx("p", { className: "text-xs text-gray-500 dark:text-gray-400 mt-1", children: "Admin Panel" })] }), user && (_jsxs("div", { className: "px-6 py-4 border-b border-gray-200 dark:border-gray-800", children: [_jsx("p", { className: "text-sm font-medium text-gray-900 dark:text-white truncate", children: user.name }), _jsx("p", { className: "text-xs text-gray-500 dark:text-gray-400 truncate", children: user.email }), _jsx("div", { className: "mt-2 flex gap-1 flex-wrap", children: user.roles.map((role) => (_jsx("span", { className: "inline-block px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded", children: role }, role))) })] })), _jsx("nav", { className: "flex-1 px-4 py-6 space-y-2 overflow-y-auto", children: visibleNavItems.map((item) => (_jsxs(Link, { to: item.href, className: `flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${isActive(item.href)
                                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 font-medium'
                                    : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}`, children: [item.icon && _jsx("span", { className: "text-lg", children: item.icon }), _jsx("span", { children: item.label })] }, item.href))) }), _jsx("div", { className: "p-4 border-t border-gray-200 dark:border-gray-800", children: _jsx("button", { onClick: () => {
                                    // Logout logic here
                                    window.location.href = '/login';
                                }, className: "w-full px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors", children: "Logout" }) })] }) }), _jsx("main", { className: "flex-1 overflow-auto", children: _jsx("div", { className: "bg-white dark:bg-gray-900 min-h-full", children: children }) })] }));
};
//# sourceMappingURL=AdminLayout.js.map