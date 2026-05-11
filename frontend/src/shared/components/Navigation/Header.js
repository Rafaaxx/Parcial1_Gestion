import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/store';
import { useUIStore } from '@/features/ui/store';
export const Header = ({ onToggleSidebar }) => {
    const navigate = useNavigate();
    const { user, logout } = useAuthStore();
    const { sidebarOpen } = useUIStore();
    const handleLogout = () => {
        logout();
        navigate('/login', { replace: true });
    };
    return (_jsx("header", { className: "sticky top-0 z-40 w-full border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm", children: _jsxs("div", { className: "flex items-center justify-between h-16 px-4 sm:px-6", children: [_jsxs("div", { className: "flex items-center gap-4", children: [_jsx("button", { onClick: onToggleSidebar, className: "md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors", "aria-label": "Toggle sidebar", children: _jsx("svg", { className: "w-6 h-6 text-gray-700 dark:text-gray-300", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M4 6h16M4 12h16M4 18h16" }) }) }), _jsx("h1", { className: "text-xl font-bold text-gray-900 dark:text-white hidden sm:block", children: "Food Store" })] }), user && (_jsxs("div", { className: "flex items-center gap-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsxs("div", { className: "text-right hidden sm:block", children: [_jsx("p", { className: "text-sm font-medium text-gray-900 dark:text-white", children: user.name }), _jsx("p", { className: "text-xs text-gray-500 dark:text-gray-400", children: user.email })] }), _jsx("div", { className: "flex gap-1 flex-wrap", children: user.roles.slice(0, 1).map((role) => (_jsx("span", { className: "hidden sm:inline-block px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded", children: role }, role))) })] }), _jsx("button", { onClick: handleLogout, className: "px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors", children: "Cerrar sesi\u00F3n" })] }))] }) }));
};
//# sourceMappingURL=Header.js.map