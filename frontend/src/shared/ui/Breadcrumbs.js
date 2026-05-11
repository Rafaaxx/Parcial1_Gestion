import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link, useLocation } from 'react-router-dom';
const PATH_LABELS = {
    '/': 'Inicio',
    '/admin': 'Administración',
    '/auth': 'Autenticación',
    '/auth/login': 'Iniciar Sesión',
    '/auth/register': 'Registrarse',
    '/productos': 'Productos',
    '/carrito': 'Carrito',
    '/perfil': 'Mi Perfil',
    '/categorias': 'Categorías',
    '/pedidos': 'Pedidos',
    '/ingredientes': 'Ingredientes',
    '/stock': 'Stock',
    '/usuarios': 'Usuarios',
    '/dashboard': 'Dashboard',
};
function getLabel(path) {
    return PATH_LABELS[path] || path.split('/').pop()?.replace(/-/g, ' ') || path;
}
export const Breadcrumbs = () => {
    const { pathname } = useLocation();
    // Don't show breadcrumbs on home
    if (pathname === '/')
        return null;
    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs = segments.map((_, index) => {
        const path = '/' + segments.slice(0, index + 1).join('/');
        return {
            label: getLabel(path),
            path,
            isActive: path === pathname,
        };
    });
    return (_jsx("nav", { "aria-label": "Breadcrumb", className: "bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800", children: _jsx("div", { className: "container mx-auto px-4 py-2", children: _jsxs("ol", { className: "flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400", children: [_jsx("li", { children: _jsx(Link, { to: "/", className: "hover:text-gray-700 dark:hover:text-gray-200 transition-colors", children: "Inicio" }) }), breadcrumbs.map((crumb) => (_jsxs("li", { className: "flex items-center gap-1", children: [_jsx("span", { className: "text-gray-300 dark:text-gray-600", children: "/" }), crumb.isActive ? (_jsx("span", { className: "text-gray-900 dark:text-gray-50 font-medium", "aria-current": "page", children: crumb.label })) : (_jsx(Link, { to: crumb.path, className: "hover:text-gray-700 dark:hover:text-gray-200 transition-colors", children: crumb.label }))] }, crumb.path)))] }) }) }));
};
export default Breadcrumbs;
//# sourceMappingURL=Breadcrumbs.js.map