import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { Navigate } from 'react-router-dom';
import { useAuthStore, userHasRole } from '@/features/auth/store';
/**
 * ProtectedRoute: Wraps a component and checks user roles before rendering
 * If user is not authenticated, redirects to fallbackPath (default: /login)
 * If user lacks required roles, redirects to unauthorizedPath (default: /unauthorized)
 */
export const ProtectedRoute = ({ children, requiredRoles, fallbackPath = '/login', unauthorizedPath = '/unauthorized', }) => {
    const { user, isAuthenticated } = useAuthStore();
    // Not authenticated -> redirect to login
    if (!isAuthenticated || !user) {
        return _jsx(Navigate, { to: fallbackPath, replace: true });
    }
    // No required roles specified -> grant access
    if (requiredRoles.length === 0) {
        return _jsx(_Fragment, { children: children });
    }
    // Check if user has any of the required roles
    if (userHasRole(user, requiredRoles)) {
        return _jsx(_Fragment, { children: children });
    }
    // User lacks required roles -> redirect to unauthorized page
    return _jsx(Navigate, { to: unauthorizedPath, replace: true });
};
//# sourceMappingURL=ProtectedRoute.js.map