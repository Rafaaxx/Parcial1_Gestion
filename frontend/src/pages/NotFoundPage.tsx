/**
 * NotFoundPage: 404 Not Found error page
 * Displayed when a route doesn't exist
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-gray-900 dark:to-gray-950 flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        {/* Error Code */}
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-yellow-600 dark:text-yellow-500">404</h1>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mt-2">Página No Encontrada</h2>
        </div>

        {/* Message */}
        <p className="text-gray-700 dark:text-gray-300 mb-8 text-lg">
          Lo sentimos, la página que buscas no existe o ha sido movida.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            onClick={() => navigate('/', { replace: true })}
            className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white font-medium rounded-lg transition-colors"
          >
            Ir a Inicio
          </button>
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white font-medium rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Volver Atrás
          </button>
        </div>
      </div>
    </div>
  );
};
