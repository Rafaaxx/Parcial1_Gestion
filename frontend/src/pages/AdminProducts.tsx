/**
 * AdminProducts — Product management with CRUD operations
 */

import React, { useState } from 'react'
import {
  useProductos,
  useCreateProducto,
  useUpdateProducto,
  useDeleteProducto,
  useCategorias,
  useUpdateProductoStock,
  useIngredientes,
} from '@/features/admin'
import type { ProductoAdmin, CategoriaAdmin, IngredienteAdmin } from '@/features/admin'

export const AdminProducts: React.FC = () => {
  const [showModal, setShowModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState<ProductoAdmin | null>(null)
  const [showStockModal, setShowStockModal] = useState<ProductoAdmin | null>(null)
  const [stockValue, setStockValue] = useState(0)

  const [form, setForm] = useState({
    nombre: '',
    descripcion: '',
    precio_base: 0,
    stock_cantidad: 0,
    disponible: true,
    categoria_ids: [] as number[],
    ingrediente_ids: [] as number[],
  })

  const { data: productos, isLoading, refetch } = useProductos()
  const { data: categorias } = useCategorias()
  const { data: ingredientes } = useIngredientes()
  const createProducto = useCreateProducto()
  const updateProducto = useUpdateProducto()
  const deleteProducto = useDeleteProducto()
  const updateStock = useUpdateProductoStock()

  const handleOpenCreate = () => {
    setEditingProduct(null)
    setForm({ nombre: '', descripcion: '', precio_base: 0, stock_cantidad: 0, disponible: true, categoria_ids: [], ingrediente_ids: [] })
    setShowModal(true)
  }

  const handleOpenEdit = (product: ProductoAdmin) => {
    // Get existing category IDs from the product (if it has categorias)
    // Handle both CategoriaBasica (from list) and CategoriaProducto (from detail)
    const existingCatIds = (product as any).categorias?.map((c: any) => {
      if ('categoria_id' in c) {
        return c.categoria_id
      }
      return c.id
    }).filter((id: number) => id) || []

    // Get existing ingredient IDs from the product
    const existingIngIds = (product as any).ingredientes?.map((i: any) => {
      // Handle both shape: { ingrediente_id } and { id } + { ingrediente: { id } }
      if (i.ingrediente_id) return i.ingrediente_id
      if (i.ingrediente?.id) return i.ingrediente.id
      return i.id
    }).filter((id: number) => id) || []

    setEditingProduct(product)
    setForm({
      nombre: product.nombre,
      descripcion: product.descripcion,
      precio_base: product.precio_base,
      stock_cantidad: product.stock_cantidad,
      disponible: product.disponible,
      categoria_ids: existingCatIds.length > 0 ? existingCatIds : [],
      ingrediente_ids: existingIngIds.length > 0 ? existingIngIds : [],
    })
    setShowModal(true)
  }

  const handleSave = async () => {
    const data = {
      nombre: form.nombre,
      descripcion: form.descripcion,
      precio_base: form.precio_base,
      stock_cantidad: form.stock_cantidad,
      disponible: form.disponible,
      ingrediente_ids: form.ingrediente_ids,
    }

    let productoId: number
    if (editingProduct) {
      const result = await updateProducto.mutateAsync({ id: editingProduct.id, data })
      productoId = editingProduct.id
    } else {
      const result = await createProducto.mutateAsync(data)
      productoId = result.id
    }

    // Update categories after create/update
    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const stored = localStorage.getItem('food-store-auth')
    const token = stored ? JSON.parse(stored).state?.token : null
    
    if (token && form.categoria_ids.length > 0) {
      // For each category, add it to the product
      for (const catId of form.categoria_ids) {
        try {
          await fetch(`${API_BASE}/api/v1/productos/${productoId}/categorias`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ categoria_id: catId, es_principal: catId === form.categoria_ids[0] }),
          })
        } catch (e) {
          console.error('Error adding category:', e)
        }
      }
    }

    setShowModal(false)
    refetch()
  }

  const handleDelete = async (id: number) => {
    if (confirm('¿Estás seguro de eliminar este producto?')) {
      await deleteProducto.mutateAsync(id)
      refetch()
    }
  }

  const handleOpenStock = (product: ProductoAdmin) => {
    setShowStockModal(product)
    setStockValue(product.stock_cantidad)
  }

  const handleUpdateStock = async () => {
    if (!showStockModal) return

    const diff = stockValue
    if (diff !== 0) {
      await updateStock.mutateAsync({ id: showStockModal.id, stock_cantidad: diff })
    }
    setShowStockModal(null)
    refetch()
  }

  const formatCurrency = (value: string) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(parseFloat(value))
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
          Gestión de Productos
        </h1>
        <button
          onClick={handleOpenCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Nuevo Producto
        </button>
      </div>

      {/* Tabla */}
      <div className="card-base overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">ID</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Nombre</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Precio</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Stock</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Categoría</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Estado</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {productos?.items.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{product.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{product.nombre}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{product.precio_base}</td>
                    <td className="px-4 py-3 text-sm">
                      <button
                        onClick={() => handleOpenStock(product)}
                        className={`font-medium hover:underline ${product.stock_cantidad <= 5 ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-gray-100'}`}
                      >
                        {product.stock_cantidad} unidades
                      </button>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">
                      {product.categorias && product.categorias.length > 0
                        ? product.categorias.map(c => {
                            // Handle both CategoriaBasica (from list endpoint) and CategoriaProducto (from detail endpoint)
                            if ('categoria' in c) {
                              return c.categoria?.nombre || ''
                            }
                            return (c as any).nombre || ''
                          }).filter(n => n).join(', ') || '-'
                        : (product.categoria_nombre || '-')}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${product.disponible ? 'bg-green-100 dark:bg-green-900 text-green-800' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'}`}>
                        {product.disponible ? 'Disponible' : 'No disponible'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={() => handleOpenEdit(product)} className="text-blue-600 dark:text-blue-400 hover:underline text-sm">
                          Editar
                        </button>
                        <button onClick={() => handleDelete(product.id)} className="text-red-600 dark:text-red-400 hover:underline text-sm">
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {productos && (
          <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500">
            Total: {productos.total} productos
          </div>
        )}
      </div>

      {/* Modal Create/Edit */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-md my-8 max-h-[28rem] flex flex-col">
            <div className="p-3 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {editingProduct ? 'Editar Producto' : 'Nuevo Producto'}
              </h2>
            </div>
            <div className="p-3 overflow-y-auto flex-1 space-y-2">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre</label>
                <input
                  type="text"
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Descripción</label>
                <textarea
                  value={form.descripcion}
                  onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                  rows={2}
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Precio</label>
                  <input
                    type="number"
                    step="0.01"
                    value={form.precio_base}
                    onChange={(e) => setForm({ ...form, precio_base: parseFloat(e.target.value) || 0 })}
                    className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Stock</label>
                  <input
                    type="number"
                    value={form.stock_cantidad}
                    onChange={(e) => setForm({ ...form, stock_cantidad: parseInt(e.target.value) || 0 })}
                    className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Categorías</label>
                <div className="space-y-1 max-h-16 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-1.5 text-xs">
                  {categorias?.items.map((cat) => (
                    <label key={cat.id} className="flex items-center gap-1 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={form.categoria_ids.includes(cat.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setForm({ ...form, categoria_ids: [...form.categoria_ids, cat.id] })
                          } else {
                            setForm({ ...form, categoria_ids: form.categoria_ids.filter(id => id !== cat.id) })
                          }
                        }}
                        className="rounded text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-700 dark:text-gray-300">{cat.nombre}</span>
                    </label>
                  ))}
                  {(!categorias || categorias.items.length === 0) && (
                    <p className="text-xs text-gray-500">Sin categorías</p>
                  )}
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Ingredientes</label>
                <div className="space-y-1 max-h-16 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded p-1.5 text-xs">
                  {ingredientes?.items.map((ing) => (
                    <label key={ing.id} className="flex items-center gap-2 cursor-pointer text-sm">
                      <input
                        type="checkbox"
                        checked={form.ingrediente_ids.includes(ing.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setForm({ ...form, ingrediente_ids: [...form.ingrediente_ids, ing.id] })
                          } else {
                            setForm({ ...form, ingrediente_ids: form.ingrediente_ids.filter(id => id !== ing.id) })
                          }
                        }}
                        className="rounded text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-700 dark:text-gray-300">{ing.nombre}</span>
                    </label>
                  ))}
                  {(!ingredientes || ingredientes.items.length === 0) && (
                    <p className="text-xs text-gray-500">No hay ingredientes disponibles</p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="disponible"
                  checked={form.disponible}
                  onChange={(e) => setForm({ ...form, disponible: e.target.checked })}
                  className="rounded"
                />
                <label htmlFor="disponible" className="text-sm text-gray-700 dark:text-gray-300">Disponible para venta</label>
              </div>
            </div>
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0 flex justify-end gap-2">
              <button onClick={() => setShowModal(false)} className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">Cancelar</button>
              <button
                onClick={handleSave}
                disabled={createProducto.isPending || updateProducto.isPending}
                className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {createProducto.isPending || updateProducto.isPending ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Stock */}
      {showStockModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Actualizar Stock: {showStockModal.nombre}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Stock actual: {showStockModal.stock_cantidad} unidades
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nuevo stock total</label>
              <input
                type="number"
                value={stockValue}
                onChange={(e) => setStockValue(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              />
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowStockModal(null)} className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg">Cancelar</button>
              <button
                onClick={handleUpdateStock}
                disabled={updateStock.isPending}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {updateStock.isPending ? 'Actualizando...' : 'Actualizar Stock'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminProducts
