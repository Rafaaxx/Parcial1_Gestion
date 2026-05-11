/**
 * ForbiddenPage — 403 Access Denied
 */

import React from 'react'
import { Link } from 'react-router-dom'

export const ForbiddenPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <span className="text-6xl mb-4">🚫</span>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2">
        Acceso denegado
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
        No tenés permisos para acceder a esta página.
      </p>
      <Link
        to="/"
        className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
      >
        Volver al inicio
      </Link>
    </div>
  )
}

export default ForbiddenPage
