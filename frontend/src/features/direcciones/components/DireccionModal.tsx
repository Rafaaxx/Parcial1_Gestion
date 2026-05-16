/**
 * DireccionModal — Modal para crear/editar direcciones
 */

import React from 'react'

interface DireccionFormData {
  alias: string
  linea1: string
}

interface DireccionModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (e: React.FormEvent) => void
  formData: DireccionFormData
  setFormData: React.Dispatch<React.SetStateAction<DireccionFormData>>
  isEditing: boolean
  isSubmitting: boolean
  error: string | null
}

export const DireccionModal: React.FC<DireccionModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  formData,
  setFormData,
  isEditing,
  isSubmitting,
  error,
}) => {
  if (!isOpen) return null

  const inputClass =
    'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'
  const labelClass = 'block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1'

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
            {isEditing ? 'Editar Dirección' : 'Nueva Dirección'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={onSubmit}>
          <div className="space-y-4">
            <div>
              <label className={labelClass} htmlFor="alias">
                Alias (opcional)
              </label>
              <input
                id="alias"
                type="text"
                value={formData.alias}
                onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
                className={inputClass}
                placeholder="Ej: Casa, Oficina"
                maxLength={50}
              />
              <p className="mt-1 text-xs text-gray-500">
                Una etiqueta para identificar esta dirección
              </p>
            </div>

            <div>
              <label className={labelClass} htmlFor="linea1">
                Dirección <span className="text-red-500">*</span>
              </label>
              <input
                id="linea1"
                type="text"
                value={formData.linea1}
                onChange={(e) => setFormData({ ...formData, linea1: e.target.value })}
                className={inputClass}
                placeholder="Ej: Calle 123, Buenos Aires"
                required
                minLength={1}
                maxLength={500}
              />
            </div>

            {error && (
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            )}
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.linea1.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg disabled:opacity-50"
            >
              {isSubmitting ? 'Guardando...' : isEditing ? 'Guardar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}