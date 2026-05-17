/**
 * IngredientCustomizer — ingredient exclusion UI
 *
 * Receives a list of ingredients and shows a toggle for each
 * removable ingredient (es_removible = true).
 * Returns an array of excluded ingredient IDs.
 */

import React, { useCallback } from 'react'
import type { IngredientInfo } from '@/features/ProductCatalog/types/catalog'

interface IngredientCustomizerProps {
  ingredientes: IngredientInfo[]
  /** Currently excluded ingredient IDs */
  excludedIds: number[]
  /** Called when the excluded set changes */
  onChange: (ids: number[]) => void
}

export const IngredientCustomizer: React.FC<IngredientCustomizerProps> = ({
  ingredientes,
  excludedIds,
  onChange,
}) => {
  const removable = ingredientes.filter((ing) => ing.es_removible)

  const handleToggle = useCallback(
    (ingredientId: number) => {
      const isExcluded = excludedIds.includes(ingredientId)
      if (isExcluded) {
        onChange(excludedIds.filter((id) => id !== ingredientId))
      } else {
        onChange([...excludedIds, ingredientId])
      }
    },
    [excludedIds, onChange]
  )

  if (removable.length === 0) return null

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Personalizar ingredientes
      </h4>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        Desmarcá los ingredientes que querés excluir
      </p>
      <div className="space-y-1.5">
        {removable.map((ing) => {
          const isExcluded = excludedIds.includes(ing.id)
          return (
            <label
              key={ing.id}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                isExcluded
                  ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                  : 'bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <input
                type="checkbox"
                checked={!isExcluded}
                onChange={() => handleToggle(ing.id)}
                className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
              />
              <span
                className={`text-sm ${
                  isExcluded
                    ? 'text-red-700 dark:text-red-400 line-through'
                    : 'text-gray-900 dark:text-gray-100'
                }`}
              >
                {ing.ingrediente.nombre}
              </span>
              {isExcluded && (
                <span className="ml-auto text-xs text-red-500 font-medium">Excluido</span>
              )}
            </label>
          )
        })}
      </div>
    </div>
  )
}

export default IngredientCustomizer
