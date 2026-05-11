/**
 * Ingredientes admin page
 * Lists all ingredients with CRUD operations (only for STOCK/ADMIN roles)
 */

import React from 'react'
import { IngredientList } from '@/features/ingredientes/ui'

export const IngredientsAdminPage: React.FC = () => {
  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Ingredientes
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Gestiona los ingredientes y sus alérgenos
        </p>
      </div>

      <IngredientList />
    </div>
  )
}
