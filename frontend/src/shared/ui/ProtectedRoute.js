import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/store';
import { Skeleton } from '@/shared/ui/Skeleton';
export const ProtectedRoute = ({ children, requiredRoles, fallback, }) => {
    const { isAuthenticated, rehydrated, user, hasRole } = useAuthStore();
    const location = useLocation();
    // Prevent flash: wait for rehydrated before checking auth
    if (!rehydrated) {
        return (_jsx("div", { className: "flex items-center justify-center min-h-[60vh]", children: _jsxs("div", { className: "space-y-4 w-full max-w-md", children: [_jsx(Skeleton, { height: "2rem", width: "40%" }), _jsx(Skeleton, { height: "1rem", count: 2 })] }) }));
    }
    // Not authenticated → redirect to login with return URL
    if (!isAuthenticated) {
        const redirectParam = encodeURIComponent(location.pathname + location.search);
        return _jsx(Navigate, { to: `/auth/login?redirect=${redirectParam}`, replace: true });
    }
    // Authenticated but missing required role → show 403
    if (requiredRoles && requiredRoles.length > 0) {
        const hasRequiredRole = requiredRoles.some((role) => hasRole(role));
        if (!hasRequiredRole) {
            if (fallback) {
                return _jsx(_Fragment, { children: fallback });
            }
            return _jsx(ForbiddenAccess, {});
        }
    }
    // Render children or Outlet
    return children ? _jsx(_Fragment, { children: children }) : _jsx(Outlet, {});
};
const ForbiddenAccess = () => (_jsxs("div", { className: "flex flex-col items-center justify-center min-h-[60vh] text-center px-4", children: [_jsx("span", { className: "text-6xl mb-4", children: "\uD83D\uDEAB" }), _jsx("h1", { className: "text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2", children: "Acceso denegado" }), _jsx("p", { className: "text-gray-600 dark:text-gray-400 mb-6 max-w-md", children: "No ten\u00E9s permisos para acceder a esta p\u00E1gina." }), _jsx("a", { href: "/", className: "px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors", children: "Volver al inicio" })] }));
export default ProtectedRoute;
//# sourceMappingURL=ProtectedRoute.js.map