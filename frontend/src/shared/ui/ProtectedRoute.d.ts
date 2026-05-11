/**
 * ProtectedRoute component for authentication and role-based access control
 */
import React from 'react';
import { type Role } from '@/features/auth/store';
interface ProtectedRouteProps {
    children?: React.ReactNode;
    requiredRoles?: Role[];
    fallback?: React.ReactNode;
}
export declare const ProtectedRoute: React.FC<ProtectedRouteProps>;
export default ProtectedRoute;
//# sourceMappingURL=ProtectedRoute.d.ts.map