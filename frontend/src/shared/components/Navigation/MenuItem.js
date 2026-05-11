import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link, useLocation } from 'react-router-dom';
export const MenuItem = ({ icon, label, path, isCollapsed = false }) => {
    const location = useLocation();
    const isActive = location.pathname === path || location.pathname.startsWith(path + '/');
    return (_jsxs(Link, { to: path, className: `flex items-center gap-3 px-4 py-2 rounded-lg transition-all ${isActive
            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 font-medium'
            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'} ${isCollapsed ? 'justify-center' : ''}`, title: isCollapsed ? label : undefined, children: [_jsx("span", { className: "text-lg flex-shrink-0", children: icon }), !isCollapsed && _jsx("span", { className: "truncate", children: label })] }));
};
//# sourceMappingURL=MenuItem.js.map