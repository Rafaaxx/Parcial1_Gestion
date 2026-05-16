/**
 * AdminStock — Stock management showing products with low stock
 */

import React, { useState } from 'react'
import { useProductos, useCategorias, useUpdateProductoStock } from '@/features/admin'

export const AdminStock: React.FC = () => {
  const [filterStock, setFilterStock] = useState<'all' | 'low'>('all')
  const [editingStock, setEditingStock] = useState<{ id: number; nombre: string; stock_cantidad: number } | null>(null)
  const [stockValue, setStockValue] = useState(0)

  const { data: productos, isLoading, refetch } = useProductos(0, 100)
  const { data: categorias } = useCategorias()
  const updateStock = useUpdateProductoStock()

  const handleEditStock = (product: { id: number; nombre: string; stock_cantidad: number }) => {
    setEditingStock(product)
    setStockValue(product.stock_cantidad)
  }

  const handleSaveStock = async () => {
    if (!editingStock) return

    const diff = stockValue
    if (diff !== 0) {
      await updateStock.mutateAsync({ id: editingStock.id, stock_cantidad: diff })
    }
    setEditingStock(null)
    refetch()
  }

  // Filtrar productos
  const filteredProducts = productos?.items.filter((p) => {
    if (filterStock === 'low') return p.stock_cantidad <= 10
    return true
  }) || []

  // Agrupar por categoría
  const productsByCategory = filteredProducts.reduce((acc, p) => {
    const catName = p.categoria_nombre || 'Sin categoría'
    if (!acc[catName]) acc[catName] = []
    acc[catName].push(p)
    return acc
  }, {} as Record<string, typeof filteredProducts>)

  const formatCurrency = (value: string) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(parseFloat(value))
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
          Gestión de Stock
        </h1>
        <div className="flex gap-2">
          <button
            onClick={() => setFilterStock('all')}
            className={`px-4 py-2 rounded-lg ${filterStock === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
          >
            Todos
          </button>
          <button
            onClick={() => setFilterStock('low')}
            className={`px-4 py-2 rounded-lg ${filterStock === 'low' ? 'bg-red-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
          >
            Stock Bajo (≤10)
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(productsByCategory).map(([category, products]) => (
            <div key={category} className="card-base">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {category} ({products.length} productos)
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">ID</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Producto</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Precio</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Stock</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {products.map((product) => (
                      <tr key={product.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{product.id}</td>
                        <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{product.nombre}</td>
                        <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{product.precio_base}</td>
                        <td className="px-4 py-3">
                          <span className={`font-medium ${product.stock_cantidad <= 5 ? 'text-red-600 dark:text-red-400' : product.stock_cantidad <= 10 ? 'text-yellow-600 dark:text-yellow-400' : 'text-gray-900 dark:text-gray-100'}`}>
                            {product.stock_cantidad} unidades
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleEditStock(product)}
                            className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                          >
                            Actualizar Stock
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal de stock */}
      {editingStock && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Actualizar Stock: {editingStock.nombre}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Stock actual: {editingStock.stock_cantidad} unidades
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
              <button onClick={() => setEditingStock(null)} className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg">Cancelar</button>
              <button
                onClick={handleSaveStock}
                disabled={updateStock.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {updateStock.isPending ? 'Actualizando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminStock
