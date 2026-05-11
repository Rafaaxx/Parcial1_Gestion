/**
 * ProtectedRoute HOC for role-based access control
 * Validates user roles before allowing access to a route
 */
import React from 'react';
interface ProtectedRouteProps {
    children: React.ReactNode;
    requiredRoles: string[];
    fallbackPath?: string;
}
/**
 * ProtectedRoute: Wraps a component and checks user roles before rendering
 * If user is not authenticated or lacks required roles, redirects to fallbackPath (default: /login)
 */
export declare const ProtectedRoute: React.FC<ProtectedRouteProps>;
export {};
//# sourceMappingURL=ProtectedRoute.d.ts.map