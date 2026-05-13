/**
 * AdminOrders — Order management with FSM (State Machine)
 * CHANGE-11: Panel de Gestión de Pedidos (Admin)
 */

import React, { useState } from 'react'
import { usePedidos, usePedidoDetail, useTransicionEstado, useCancelarPedido, getTransicionesDisponibles } from '@/features/pedidos'
import { OrderFilters, OrderDetailModal } from '@/features/pedidos/components'
import { useAuthStore } from '@/features/auth/store'
import { Button, Toast } from '@/shared/ui'
import {
  PedidoListItem,
  Pedido,
  PedidoFilters,
  EstadoPedido,
  ESTADO_LABELS,
  ESTADO_COLORS,
  esEstadoTerminal,
} from '@/features/pedidos/types'

// Componente para mostrar el badge de estado
const EstadoBadge: React.FC<{ estado: string }> = ({ estado }) => {
  const colorClass = ESTADO_COLORS[estado as EstadoPedido] || 'bg-gray-100 text-gray-800'
  const label = ESTADO_LABELS[estado as EstadoPedido] || estado

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}
    >
      {label}
    </span>
  )
}

// Componente para mostrar info del cliente
const ClienteCell: React.FC<{ pedido: PedidoListItem }> = ({ pedido }) => {
  if (!pedido.cliente) {
    return <span className="text-gray-400">-</span>
  }

  const { nombre, email } = pedido.cliente
  const displayName = nombre || email

  return (
    <div className="text-sm">
      {nombre && <div className="font-medium text-gray-900 dark:text-gray-100">{nombre}</div>}
      <div className="text-gray-500 dark:text-gray-400">{email}</div>
    </div>
  )
}

// Componente principal
export const AdminOrders: React.FC = () => {
  const [skip, setSkip] = useState(0)
  const limit = 20

  // State for filters
  const [filtros, setFiltros] = useState<PedidoFilters>({})

  // State for modal
  const [selectedPedidoId, setSelectedPedidoId] = useState<number | null>(null)
  const [detailModalOpen, setDetailModalOpen] = useState(false)

  // DEBUG: Auto-open first pedido when data loads
  React.useEffect(() => {
    if (data?.items?.length && !selectedPedidoId && !detailModalOpen) {
      console.log('[DEBUG] Auto-opening first pedido')
      setSelectedPedidoId(data.items[0].id)
      setDetailModalOpen(true)
    }
  }, [data, selectedPedidoId, detailModalOpen])

  // Queries
  const { data, isLoading, error, refetch } = usePedidos(skip, limit, filtros)
  const { data: pedidoDetalle, isLoading: detailLoading } = usePedidoDetail(selectedPedidoId || 0)
  console.log('[DEBUG] pedidoDetalle:', pedidoDetalle)
  console.log('[DEBUG] detailLoading:', detailLoading)
  console.log('[DEBUG] selectedPedidoId:', selectedPedidoId)
  console.log('[DEBUG] detailModalOpen:', detailModalOpen)

  const transicionMutation = useTransicionEstado()
  const cancelarMutation = useCancelarPedido()

  // Estado para toast
  const [toast, setToast] = useState<{
    open: boolean
    type: 'success' | 'error'
    message: string
  }>({
    open: false,
    type: 'success',
    message: '',
  })

  // Mostrar toast de error de mutación
  React.useEffect(() => {
    if (transicionMutation.isError) {
      setToast({
        open: true,
        type: 'error',
        message: (transicionMutation.error as Error)?.message || 'Error al cambiar estado',
      })
    }
  }, [transicionMutation.isError, transicionMutation.error])

  // Reset pagination when filters change
  const handleFiltrosChange = (newFiltros: PedidoFilters) => {
    setFiltros(newFiltros)
    setSkip(0) // Reset to first page
  }

  // Open detail modal
  const handleRowClick = (pedido: PedidoListItem) => {
    alert('Click detected on pedido: ' + pedido.id)
    setSelectedPedidoId(pedido.id)
    setDetailModalOpen(true)
  }

  // Close detail modal
  const handleCloseDetail = () => {
    setDetailModalOpen(false)
    setSelectedPedidoId(null)
    refetch() // Refresh list after potential changes
  }

  // Calcular paginación
  const total = data?.total || 0
  const hasNext = skip + limit < total
  const hasPrev = skip > 0

  // Formatear precio
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(price)
  }

  // Formatear fecha
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('es-AR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
        Gestión de Pedidos
      </h1>

      {/* Filtros */}
      <OrderFilters filtros={filtros} onChange={handleFiltrosChange} />

      {/* Tabla de pedidos */}
      <div className="card-base overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Cargando pedidos...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">
            Error al cargar pedidos: {(error as Error).message}
          </div>
        ) : !data?.items.length ? (
          <div className="p-12 text-center">
            <span className="text-5xl block mb-4">📋</span>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-2">
              No hay pedidos
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {Object.keys(filtros).length > 0
                ? 'No hay pedidos que coincidan con los filtros aplicados'
                : 'Los pedidos aparecerán aquí cuando se creen.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Cliente
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Total
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Fecha
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {data.items.map((pedido) => (
                  <tr
                    key={pedido.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer"
                    onClick={() => alert('Click on pedido ' + pedido.id)}
                  >
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-50">
                      #{pedido.id}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <ClienteCell pedido={pedido} />
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <EstadoBadge estado={pedido.estado_codigo} />
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatPrice(pedido.total)}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(pedido.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Paginación */}
        {total > 0 && (
          <div className="px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {total === 0
                ? 'Sin resultados'
                : `Mostrando ${skip + 1} - ${Math.min(skip + limit, total)} de ${total}`}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={!hasPrev}
                onClick={() => setSkip(Math.max(0, skip - limit))}
              >
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={!hasNext}
                onClick={() => setSkip(skip + limit)}
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Modal de detalle */}
      <OrderDetailModal
        pedido={detailModalOpen && selectedPedidoId ? pedidoDetalle : null}
        open={detailModalOpen}
        onClose={handleCloseDetail}
      />

      {/* Toast notifications */}
      <Toast
        open={toast.open}
        onClose={() => setToast((prev) => ({ ...prev, open: false }))}
        type={toast.type}
        message={toast.message}
      />
    </div>
  )
}

export default AdminOrders