/**
 * Admin dashboard page
 */

import React from 'react';
import { useAuthStore } from '@/features/auth/store';

export const AdminDashboardPage: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Bienvenido al panel de administración, {user?.name}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Ingredientes</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Gestiona los ingredientes de tu sistema
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Categorías</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Organiza productos por categoría
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Productos</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">Crea y modifica tus productos</p>
        </div>
      </div>
    </div>
  );
};
