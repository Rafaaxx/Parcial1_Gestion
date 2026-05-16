/**
 * AdminCategories — Category management with CRUD operations
 */

import React, { useState } from 'react'
import { useCategorias, useCreateCategoria, useUpdateCategoria, useDeleteCategoria } from '@/features/admin'
import type { CategoriaAdmin } from '@/features/admin'

export const AdminCategories: React.FC = () => {
  const [showModal, setShowModal] = useState(false)
  const [editingCategory, setEditingCategory] = useState<CategoriaAdmin | null>(null)
  const [form, setForm] = useState({ nombre: '', descripcion: '', padre_id: undefined as number | undefined })

  const { data: categorias, isLoading, refetch } = useCategorias()
  const createCategoria = useCreateCategoria()
  const updateCategoria = useUpdateCategoria()
  const deleteCategoria = useDeleteCategoria()

  const handleOpenCreate = () => {
    setEditingCategory(null)
    setForm({ nombre: '', descripcion: '', padre_id: undefined })
    setShowModal(true)
  }

  const handleOpenEdit = (category: CategoriaAdmin) => {
    setEditingCategory(category)
    setForm({ nombre: category.nombre, descripcion: category.descripcion, padre_id: category.padre_id || undefined })
    setShowModal(true)
  }

  const handleSave = async () => {
    const data = { nombre: form.nombre, descripcion: form.descripcion, padre_id: form.padre_id }

    if (editingCategory) {
      await updateCategoria.mutateAsync({ id: editingCategory.id, data })
    } else {
      await createCategoria.mutateAsync(data)
    }

    setShowModal(false)
    refetch()
  }

  const handleDelete = async (id: number) => {
    if (confirm('¿Estás seguro de eliminar esta categoría?')) {
      await deleteCategoria.mutateAsync(id)
      refetch()
    }
  }

  // Construir árbol de categorías
  const buildTree = (cats?: CategoriaAdmin[]) => {
    if (!cats) return []
    const rootCategories = cats.filter((c) => !c.padre_id)
    return rootCategories.map((root) => ({
      ...root,
      children: cats.filter((c) => c.padre_id === root.id),
    }))
  }

  const tree = categorias?.items ? buildTree(categorias.items) : []

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
          Gestión de Categorías
        </h1>
        <button
          onClick={handleOpenCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Nueva Categoría
        </button>
      </div>

      {/* Lista de categorías en árbol */}
      <div className="card-base">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : (
          <div className="p-4 space-y-2">
            {tree.map((category) => (
              <div key={category.id} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">{category.nombre}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{category.descripcion}</p>
                    <div className="flex gap-2 mt-1">
                      <span className={`px-2 py-1 text-xs rounded ${category.activo ? 'bg-green-100 dark:bg-green-900 text-green-800' : 'bg-red-100 dark:bg-red-900 text-red-800'}`}>
                        {category.activo ? 'Activa' : 'Inactiva'}
                      </span>
                      {category.hijo_ids.length > 0 && (
                        <span className="px-2 py-1 text-xs rounded bg-blue-100 dark:bg-blue-900 text-blue-800">
                          {category.hijo_ids.length} subcategorías
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleOpenEdit(category)} className="text-blue-600 dark:text-blue-400 hover:underline text-sm">
                      Editar
                    </button>
                    <button onClick={() => handleDelete(category.id)} className="text-red-600 dark:text-red-400 hover:underline text-sm">
                      Eliminar
                    </button>
                  </div>
                </div>
                {category.children.length > 0 && (
                  <div className="pl-8 border-t border-gray-200 dark:border-gray-700">
                    {category.children.map((child) => (
                      <div key={child.id} className="flex items-center justify-between p-3 border-b border-gray-100 dark:border-gray-700 last:border-0">
                        <div>
                          <span className="text-gray-900 dark:text-gray-100">{child.nombre}</span>
                          <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">- {child.descripcion}</span>
                        </div>
                        <div className="flex gap-2">
                          <button onClick={() => handleOpenEdit(child)} className="text-blue-600 dark:text-blue-400 hover:underline text-sm">
                            Editar
                          </button>
                          <button onClick={() => handleDelete(child.id)} className="text-red-600 dark:text-red-400 hover:underline text-sm">
                            Eliminar
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-4">
              {editingCategory ? 'Editar Categoría' : 'Nueva Categoría'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre</label>
                <input
                  type="text"
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Descripción</label>
                <textarea
                  value={form.descripcion}
                  onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Categoría padre (opcional)</label>
                <select
                  value={form.padre_id || ''}
                  onChange={(e) => setForm({ ...form, padre_id: e.target.value ? parseInt(e.target.value) : undefined })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                >
                  <option value="">Ninguna (categoría raíz)</option>
                  {(categorias?.items ?? [])
                    .filter((c) => c.id !== editingCategory?.id && !c.padre_id)
                    .map((cat) => (
                      <option key={cat.id} value={cat.id}>{cat.nombre}</option>
                    ))}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg">Cancelar</button>
              <button
                onClick={handleSave}
                disabled={createCategoria.isPending || updateCategoria.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {createCategoria.isPending || updateCategoria.isPending ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminCategories
