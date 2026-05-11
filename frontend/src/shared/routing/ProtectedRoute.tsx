/**
 * ProtectedRoute HOC for role-based access control
 * Validates user roles before allowing access to a route
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore, userHasRole } from '@/features/auth/store';

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
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles,
  fallbackPath = '/login',
  unauthorizedPath = '/unauthorized',
}) => {
  const { user, isAuthenticated } = useAuthStore();

  // Not authenticated -> redirect to login
  if (!isAuthenticated || !user) {
    return <Navigate to={fallbackPath} replace />;
  }

  // No required roles specified -> grant access
  if (requiredRoles.length === 0) {
    return <>{children}</>;
  }

  // Check if user has any of the required roles
  if (userHasRole(user, requiredRoles)) {
    return <>{children}</>;
  }

  // User lacks required roles -> redirect to unauthorized page
  return <Navigate to={unauthorizedPath} replace />;
};
