import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * UserDropdown component for authenticated user menu
 */
import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
import { useAuthStore } from '@/features/auth/store';
import { apiClient } from '@/shared/http/client';
export const UserDropdown = () => {
    const { user, logout } = useAuth();
    const [open, setOpen] = useState(false);
    const dropdownRef = useRef(null);
    const navigate = useNavigate();
    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);
    const handleLogout = async () => {
        try {
            const refreshToken = useAuthStore.getState().refreshToken;
            // Fire-and-forget logout API call with refresh_token
            await apiClient.post('/auth/logout', { refresh_token: refreshToken });
        }
        catch {
            // Ignore errors - we're logging out anyway
        }
        logout();
        setOpen(false);
        navigate('/');
    };
    if (!user)
        return null;
    const initials = user.name.charAt(0).toUpperCase();
    return (_jsxs("div", { className: "relative", ref: dropdownRef, children: [_jsxs("button", { onClick: () => setOpen(!open), className: "flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors", "aria-label": "Men\u00FA de usuario", "aria-expanded": open, children: [_jsx("div", { className: "w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-sm font-semibold", children: initials }), _jsx("svg", { className: `w-4 h-4 text-gray-500 dark:text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`, fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M19 9l-7 7-7-7" }) })] }), open && (_jsxs("div", { className: "absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50", children: [_jsxs("div", { className: "px-4 py-3 border-b border-gray-100 dark:border-gray-700", children: [_jsx("p", { className: "text-sm font-medium text-gray-900 dark:text-gray-50 truncate", children: user.name }), _jsx("p", { className: "text-xs text-gray-500 dark:text-gray-400 truncate", children: user.email })] }), _jsx("div", { className: "py-1", children: _jsx(Link, { to: "/perfil", onClick: () => setOpen(false), className: "block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors", children: "Mi Perfil" }) }), _jsx("div", { className: "border-t border-gray-100 dark:border-gray-700 py-1", children: _jsx("button", { onClick: handleLogout, className: "w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors", children: "Cerrar Sesi\u00F3n" }) })] }))] }));
};
export default UserDropdown;
//# sourceMappingURL=UserDropdown.js.map