/**
 * ProtectedRoute HOC for role-based access control
 * Validates user roles before allowing access to a route
 */
import React from 'react';
interface ProtectedRouteProps {
    children: React.ReactNode;
    requiredRoles: string[];
    fallbackPath?: string;
    unauthorizedPath?: string;
}
/**
 * ProtectedRoute: Wraps a component and checks user roles before rendering
 * If user is not authenticated, redirects to fallbackPath (default: /login)
 * If user lacks required roles, redirects to unauthorizedPath (default: /unauthorized)
 */
export declare const ProtectedRoute: React.FC<ProtectedRouteProps>;
export {};
//# sourceMappingURL=ProtectedRoute.d.ts.map