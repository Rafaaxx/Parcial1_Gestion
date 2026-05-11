/**
 * UnauthorizedPage: 403 Forbidden error page
 * Displayed when user lacks required permissions
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

export const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 dark:from-gray-900 dark:to-gray-950 flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        {/* Error Code */}
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-red-600 dark:text-red-500">403</h1>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mt-2">Acceso Prohibido</h2>
        </div>

        {/* Message */}
        <p className="text-gray-700 dark:text-gray-300 mb-8 text-lg">
          No tienes permiso para acceder a este recurso. Tu rol actual no autoriza este acceso.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            onClick={() => navigate('/app/dashboard', { replace: true })}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
          >
            Ir al Dashboard
          </button>
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white font-medium rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Volver Atrás
          </button>
        </div>

        {/* Help Text */}
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-8">
          Si crees que esto es un error, por favor contacta al administrador.
        </p>
      </div>
    </div>
  );
};
