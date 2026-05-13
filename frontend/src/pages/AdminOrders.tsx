/**
 * AdminOrders — Order management with FSM (State Machine)
 */

import React, { useState } from 'react'
import { usePedidos, useTransicionEstado, useCancelarPedido, getTransicionesDisponibles } from '@/features/pedidos'
import { useAuthStore } from '@/features/auth/store'
import { Button, Modal, Textarea, Toast } from '@/shared/ui'
import {
  PedidoListItem,
  EstadoPedido,
  ESTADO_LABELS,
  ESTADO_COLORS,
  esEstadoTerminal,
  TransicionAction,
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

// Componente para los botones de acción
const AccionesPedido: React.FC<{
  pedido: PedidoListItem
  onOpenCancel: (pedido: PedidoListItem) => void
}> = ({ pedido, onOpenCancel }) => {
  const { user } = useAuthStore()
  const transicionMutation = useTransicionEstado()

  const userRoles = user?.roles || []
  const transiciones = getTransicionesDisponibles(pedido.estado_codigo, userRoles)

  // Si es estado terminal, no hay acciones
  if (esEstadoTerminal(pedido.estado_codigo)) {
    return (
      <span className="text-sm text-gray-500">Sin acciones disponibles</span>
    )
  }

  return (
    <div className="flex gap-2 flex-wrap">
      {transiciones.map((transicion, idx) => (
        <Button
          key={idx}
          size="sm"
          variant={transicion.nuevo_estado === 'CANCELADO' ? 'danger' : 'primary'}
          onClick={() => {
            if (transicion.requires_motivo && transicion.nuevo_estado === 'CANCELADO') {
              // Abrir modal de cancelación
              onOpenCancel(pedido)
            } else {
              // Ejecutar transición directa
              transicionMutation.mutate({
                pedidoId: pedido.id,
                data: { nuevo_estado: transicion.nuevo_estado },
              })
            }
          }}
          disabled={transicionMutation.isPending}
        >
          {transicion.label}
        </Button>
      ))}
    </div>
  )
}

// Componente principal
export const AdminOrders: React.FC = () => {
  const [skip, setSkip] = useState(0)
  const limit = 20

  // Queries y mutations
  const { data, isLoading, error } = usePedidos(skip, limit)
  const transicionMutation = useTransicionEstado()
  const cancelarMutation = useCancelarPedido()

  // Estado para el modal de cancelación
  const [cancelModal, setCancelModal] = useState<{
    open: boolean
    pedido: PedidoListItem | null
    motivo: string
    error: string
  }>({
    open: false,
    pedido: null,
    motivo: '',
    error: '',
  })

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

  // Handlers
  const handleOpenCancel = (pedido: PedidoListItem) => {
    setCancelModal({
      open: true,
      pedido,
      motivo: '',
      error: '',
    })
  }

  const handleCloseCancel = () => {
    setCancelModal({
      open: false,
      pedido: null,
      motivo: '',
      error: '',
    })
  }

  const handleConfirmCancel = () => {
    if (!cancelModal.pedido || !cancelModal.motivo.trim()) {
      setCancelModal((prev) => ({
        ...prev,
        error: 'El motivo es obligatorio',
      }))
      return
    }

    // Ejecutar cancelación
    cancelarMutation.mutate(
      {
        pedidoId: cancelModal.pedido.id,
        motivo: cancelModal.motivo,
      },
      {
        onSuccess: () => {
          handleCloseCancel()
          setToast({
            open: true,
            type: 'success',
            message: `Pedido #${cancelModal.pedido?.id} cancelado exitosamente`,
          })
        },
        onError: (error: Error) => {
          setToast({
            open: true,
            type: 'error',
            message: error.message || 'Error al cancelar el pedido',
          })
        },
      }
    )
  }

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

  // Calcular paginación
  const total = data?.total || 0
  const hasNext = skip + limit < total
  const hasPrev = skip > 0

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

  // Formatear precio
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(price)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
        Gestión de Pedidos
      </h1>

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
              Los pedidos aparecerán aquí cuando se creen.
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
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Total
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Fecha
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {data.items.map((pedido) => (
                  <tr
                    key={pedido.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-800/50"
                  >
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-50">
                      #{pedido.id}
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
                    <td className="px-4 py-4 whitespace-nowrap">
                      <AccionesPedido
                        pedido={pedido}
                        onOpenCancel={handleOpenCancel}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Paginación */}
        {total > limit && (
          <div className="px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Mostrando {skip + 1} - {Math.min(skip + limit, total)} de {total}
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

      {/* Modal de cancelación */}
      <Modal
        open={cancelModal.open}
        onClose={handleCloseCancel}
        title="Cancelar Pedido"
        actions={
          <>
            <Button variant="outline" onClick={handleCloseCancel}>
              Cancelar
            </Button>
            <Button
              variant="danger"
              onClick={handleConfirmCancel}
              disabled={cancelarMutation.isPending}
            >
              {cancelarMutation.isPending ? 'Cancelando...' : 'Confirmar'}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            ¿Estás seguro de que deseas cancelar el pedido #
            <strong>{cancelModal.pedido?.id}</strong>?
          </p>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Motivo de cancelación <span className="text-red-500">*</span>
            </label>
            <Textarea
              value={cancelModal.motivo}
              onChange={(e) =>
                setCancelModal((prev) => ({
                  ...prev,
                  motivo: e.target.value,
                  error: '',
                }))
              }
              placeholder="Ingrese el motivo de la cancelación..."
              rows={3}
              error={cancelModal.error}
            />
          </div>
        </div>
      </Modal>

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