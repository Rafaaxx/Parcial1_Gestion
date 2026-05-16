/**
 * ProtectedRoute component for authentication and role-based access control
 */

import React from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore, userHasRole, type Role } from '@/features/auth/store'
import { Skeleton } from '@/shared/ui/Skeleton'

interface ProtectedRouteProps {
  children?: React.ReactNode
  requiredRoles?: Role[]
  fallback?: React.ReactNode
}

/**
 * ProtectedRoute: guards routes by authentication + role.
 *
 * 1. Waits for rehydration (prevents flash).
 * 2. Checks authentication — redirects to login with return URL.
 * 3. If roles are required, checks user has at least one — shows ForbiddenAccess otherwise.
 * 4. Renders children or Outlet.
 *
 * IMPORTANT: isAuthenticated can be true BEFORE user data loads
 * (token rehydrated from localStorage but /auth/me not yet called).
 * We use the standalone userHasRole(user, roles) which safely handles null user.
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles,
  fallback,
}) => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const rehydrated = useAuthStore((s) => s.rehydrated)
  const user = useAuthStore((s) => s.user)
  const location = useLocation()

  // Prevent flash: wait for rehydrated before checking auth
  if (!rehydrated) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="space-y-4 w-full max-w-md">
          <Skeleton height="2rem" width="40%" />
          <Skeleton height="1rem" count={2} />
        </div>
      </div>
    )
  }

  // Not authenticated → redirect to login with return URL
  if (!isAuthenticated) {
    const redirectParam = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/auth/login?redirect=${redirectParam}`} replace />
  }

  // Authenticated but user profile still loading (restoreSession in progress)
  // Wait instead of redirecting — avoids premature redirect loop
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="space-y-4 w-full max-w-md">
          <Skeleton height="2rem" width="40%" />
          <Skeleton height="1rem" count={2} />
        </div>
      </div>
    )
  }

  // Authenticated but missing required role → show 403
  if (requiredRoles && requiredRoles.length > 0) {
    const hasRequiredRole = userHasRole(user, requiredRoles)
    if (!hasRequiredRole) {
      if (fallback) {
        return <>{fallback}</>
      }
      return <ForbiddenAccess />
    }
  }

  // Render children or Outlet
  return children ? <>{children}</> : <Outlet />
}

const ForbiddenAccess: React.FC = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
    <span className="text-6xl mb-4">🚫</span>
    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2">
      Acceso denegado
    </h1>
    <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
      No tenés permisos para acceder a esta página.
    </p>
    <a
      href="/"
      className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
    >
      Volver al inicio
    </a>
  </div>
)

export default ProtectedRoute
