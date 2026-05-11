/**
 * Breadcrumbs component for navigation hierarchy
 */

import React from 'react'
import { Link, useLocation } from 'react-router-dom'

const PATH_LABELS: Record<string, string> = {
  '/': 'Inicio',
  '/admin': 'Administración',
  '/auth': 'Autenticación',
  '/auth/login': 'Iniciar Sesión',
  '/auth/register': 'Registrarse',
  '/productos': 'Productos',
  '/carrito': 'Carrito',
  '/perfil': 'Mi Perfil',
  '/categorias': 'Categorías',
  '/pedidos': 'Pedidos',
  '/ingredientes': 'Ingredientes',
  '/stock': 'Stock',
  '/usuarios': 'Usuarios',
  '/dashboard': 'Dashboard',
}

function getLabel(path: string): string {
  return PATH_LABELS[path] || path.split('/').pop()?.replace(/-/g, ' ') || path
}

export const Breadcrumbs: React.FC = () => {
  const { pathname } = useLocation()

  // Don't show breadcrumbs on home
  if (pathname === '/') return null

  const segments = pathname.split('/').filter(Boolean)
  const breadcrumbs = segments.map((_, index) => {
    const path = '/' + segments.slice(0, index + 1).join('/')
    return {
      label: getLabel(path),
      path,
      isActive: path === pathname,
    }
  })

  return (
    <nav aria-label="Breadcrumb" className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
      <div className="container mx-auto px-4 py-2">
        <ol className="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
          <li>
            <Link
              to="/"
              className="hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
            >
              Inicio
            </Link>
          </li>
          {breadcrumbs.map((crumb) => (
            <li key={crumb.path} className="flex items-center gap-1">
              <span className="text-gray-300 dark:text-gray-600">/</span>
              {crumb.isActive ? (
                <span className="text-gray-900 dark:text-gray-50 font-medium" aria-current="page">
                  {crumb.label}
                </span>
              ) : (
                <Link
                  to={crumb.path}
                  className="hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
                >
                  {crumb.label}
                </Link>
              )}
            </li>
          ))}
        </ol>
      </div>
    </nav>
  )
}

export default Breadcrumbs
