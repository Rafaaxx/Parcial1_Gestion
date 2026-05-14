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
} from '@/features/admin'
import type { ProductoAdmin, CategoriaAdmin } from '@/features/admin'

export const AdminProducts: React.FC = () => {
  const [showModal, setShowModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState<ProductoAdmin | null>(null)
  const [showStockModal, setShowStockModal] = useState<ProductoAdmin | null>(null)
  const [stockValue, setStockValue] = useState(0)

  const [form, setForm] = useState({
    nombre: '',
    descripcion: '',
    precio: '',
    stock: '',
    disponible: true,
    categoria_id: 0,
  })

  const { data: productos, isLoading, refetch } = useProductos()
  const { data: categorias } = useCategorias()
  const createProducto = useCreateProducto()
  const updateProducto = useUpdateProducto()
  const deleteProducto = useDeleteProducto()
  const updateStock = useUpdateProductoStock()

  const handleOpenCreate = () => {
    setEditingProduct(null)
    setForm({ nombre: '', descripcion: '', precio: '', stock: '', disponible: true, categoria_id: 0 })
    setShowModal(true)
  }

  const handleOpenEdit = (product: ProductoAdmin) => {
    setEditingProduct(product)
    setForm({
      nombre: product.nombre,
      descripcion: product.descripcion,
      precio: product.precio_base,
      stock: String(product.stock_cantidad),
      disponible: product.disponible,
      categoria_id: product.categoria_id,
    })
    setShowModal(true)
  }

  const handleSave = async () => {
    const data = {
      nombre: form.nombre,
      descripcion: form.descripcion,
      precio: parseFloat(form.precio),
      stock: parseInt(form.stock),
      disponible: form.disponible,
      categoria_id: form.categoria_id,
    }

    if (editingProduct) {
      await updateProducto.mutateAsync({ id: editingProduct.id, data })
    } else {
      await createProducto.mutateAsync(data)
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

    const diff = stockValue - showStockModal.stock_cantidad
    if (diff !== 0) {
      await updateStock.mutateAsync({ id: showStockModal.id, cantidad: diff })
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
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{formatCurrency(product.precio_base)}</td>
                    <td className="px-4 py-3 text-sm">
                      <button
                        onClick={() => handleOpenStock(product)}
                        className={`font-medium hover:underline ${product.stock_cantidad <= 5 ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-gray-100'}`}
                      >
                        {product.stock_cantidad} unidades
                      </button>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{product.categoria_nombre || '-'}</td>
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-lg">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-4">
              {editingProduct ? 'Editar Producto' : 'Nuevo Producto'}
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
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Precio</label>
                  <input
                    type="number"
                    step="0.01"
                    value={form.precio}
                    onChange={(e) => setForm({ ...form, precio: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Stock</label>
                  <input
                    type="number"
                    value={form.stock}
                    onChange={(e) => setForm({ ...form, stock: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Categoría</label>
                <select
                  value={form.categoria_id}
                  onChange={(e) => setForm({ ...form, categoria_id: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                >
                  <option value={0}>Seleccionar categoría</option>
                  {categorias?.items.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.nombre}</option>
                  ))}
                </select>
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
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg">Cancelar</button>
              <button
                onClick={handleSave}
                disabled={createProducto.isPending || updateProducto.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
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
