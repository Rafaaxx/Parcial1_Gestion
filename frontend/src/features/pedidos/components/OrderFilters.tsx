/**
 * OrderFilters - Filtros para el listado de pedidos
 */

import React, { useState, useEffect } from 'react'
import { Button, Input } from '@/shared/ui'
import { EstadoPedido, ESTADO_LABELS, PedidoFilters } from '../types'

interface OrderFiltersProps {
  filtros: PedidoFilters
  onChange: (filtros: PedidoFilters) => void
}

const ESTADOS_OPCIONES: { value: string; label: string }[] = [
  { value: '', label: 'Todos los estados' },
  ...Object.entries(ESTADO_LABELS).map(([value, label]) => ({
    value,
    label,
  })),
]

export const OrderFilters: React.FC<OrderFiltersProps> = ({ filtros, onChange }) => {
  const [estado, setEstado] = useState(filtros.estado || '')
  const [desde, setDesde] = useState(filtros.desde || '')
  const [hasta, setHasta] = useState(filtros.hasta || '')
  const [busqueda, setBusqueda] = useState(filtros.busqueda || '')

  // Sync with parent filtros prop
  useEffect(() => {
    setEstado(filtros.estado || '')
    setDesde(filtros.desde || '')
    setHasta(filtros.hasta || '')
    setBusqueda(filtros.busqueda || '')
  }, [filtros.estado, filtros.desde, filtros.hasta, filtros.busqueda])

  const handleChange = (newFiltros: Partial<PedidoFilters>) => {
    const updated = {
      ...filtros,
      ...newFiltros,
    }
    // Clear empty values
    if (!updated.estado) delete updated.estado
    if (!updated.desde) delete updated.desde
    if (!updated.hasta) delete updated.hasta
    if (!updated.busqueda) delete updated.busqueda
    
    onChange(updated)
  }

  const handleLimpiar = () => {
    setEstado('')
    setDesde('')
    setHasta('')
    setBusqueda('')
    onChange({})
  }

  const tieneFiltros = estado || desde || hasta || busqueda

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Estado dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Estado
          </label>
          <select
            value={estado}
            onChange={(e) => handleChange({ estado: e.target.value || undefined })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {ESTADOS_OPCIONES.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Fecha desde */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Desde
          </label>
          <input
            type="date"
            value={desde}
            onChange={(e) => handleChange({ desde: e.target.value || undefined })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Fecha hasta */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Hasta
          </label>
          <input
            type="date"
            value={hasta}
            onChange={(e) => handleChange({ hasta: e.target.value || undefined })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Búsqueda */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Buscar
          </label>
          <input
            type="text"
            value={busqueda}
            onChange={(e) => handleChange({ busqueda: e.target.value || undefined })}
            placeholder="ID o cliente..."
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Botón limpiar */}
        <div className="flex items-end">
          <Button
            variant="secondary"
            onClick={handleLimpiar}
            disabled={!tieneFiltros}
            className="w-full"
          >
            Limpiar
          </Button>
        </div>
      </div>
    </div>
  )
}

export default OrderFilters