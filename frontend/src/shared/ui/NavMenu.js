import { jsx as _jsx } from "react/jsx-runtime";
import { NavLink } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
const PUBLIC_ITEMS = [
    { label: 'Catálogo', path: '/productos' },
];
const AUTH_ITEMS = [
    { label: 'Catálogo', path: '/productos' },
];
const ROLE_ITEMS = {
    CLIENT: [
        { label: 'Catálogo', path: '/productos' },
        { label: 'Mi Carrito', path: '/carrito' },
        { label: 'Mis Pedidos', path: '/pedidos' },
        { label: 'Mi Perfil', path: '/perfil' },
    ],
    STOCK: [
        { label: 'Productos', path: '/admin/productos' },
        { label: 'Categorías', path: '/admin/categorias' },
        { label: 'Ingredientes', path: '/admin/stock' },
        { label: 'Stock', path: '/admin/stock' },
    ],
    PEDIDOS: [
        { label: 'Panel de Pedidos', path: '/admin/pedidos' },
    ],
    ADMIN: [
        { label: 'Dashboard', path: '/admin' },
        { label: 'Usuarios', path: '/admin/usuarios' },
        { label: 'Productos', path: '/admin/productos' },
        { label: 'Categorías', path: '/admin/categorias' },
        { label: 'Pedidos', path: '/admin/pedidos' },
        { label: 'Stock', path: '/admin/stock' },
    ],
};
function getAllowedItems(user) {
    if (!user)
        return PUBLIC_ITEMS;
    const allowed = new Map();
    // Add all items the user has roles for
    for (const role of user.roles) {
        const items = ROLE_ITEMS[role];
        if (items) {
            for (const item of items) {
                allowed.set(item.path, item);
            }
        }
    }
    // Admin always gets all
    if (user.roles.includes('ADMIN')) {
        for (const items of Object.values(ROLE_ITEMS)) {
            for (const item of items) {
                allowed.set(item.path, item);
            }
        }
    }
    return Array.from(allowed.values());
}
export const NavMenu = ({ isMobile = false, onItemClick }) => {
    const { user } = useAuth();
    const items = getAllowedItems(user);
    const linkClass = ({ isActive }) => `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
        ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-50'}`;
    if (isMobile) {
        return (_jsx("nav", { className: "flex flex-col gap-1 px-2 py-4", children: items.map((item) => (_jsx(NavLink, { to: item.path, end: true, className: linkClass, onClick: onItemClick, children: item.label }, item.path))) }));
    }
    return (_jsx("nav", { className: "hidden md:flex items-center gap-1", children: items.map((item) => (_jsx(NavLink, { to: item.path, end: true, className: linkClass, children: item.label }, item.path))) }));
};
export default NavMenu;
//# sourceMappingURL=NavMenu.js.map