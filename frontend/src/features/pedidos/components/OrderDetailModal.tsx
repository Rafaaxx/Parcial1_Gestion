/**
 * OrderDetailModal - Modal con tabs para ver detalle del pedido
 */

import React, { useState } from 'react'
import { Modal, Button } from '@/shared/ui'
import { Pedido, ESTADO_LABELS, ESTADO_COLORS, ClienteInfo, EstadoPedido } from '../types'
import { HistorialTimeline } from './HistorialTimeline'
import { TransicionAction, getTransicionesDisponibles } from '../hooks'
import { useAuthStore } from '@/features/auth/store'
import { useTransicionEstado, useCancelarPedido } from '../hooks'

interface OrderDetailModalProps {
  pedido: Pedido | null
  open: boolean
  onClose: () => void
}

type TabType = 'resumen' | 'lineas' | 'historial' | 'pago'

export const OrderDetailModal: React.FC<OrderDetailModalProps> = ({
  pedido,
  open,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('resumen')
  const { user } = useAuthStore()
  const transicionMutation = useTransicionEstado()
  const cancelarMutation = useCancelarPedido()

  // Estado para modal de cancelación
  const [cancelModal, setCancelModal] = useState<{
    open: boolean
    motivo: string
    error: string
  }>({
    open: false,
    motivo: '',
    error: '',
  })

  if (!pedido) return null

  const userRoles = user?.roles || []
  const transiciones = getTransicionesDisponibles(pedido.estado_codigo, userRoles)

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(price)
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('es-AR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const handleTransicion = (transicion: TransicionAction) => {
    if (transicion.requires_motivo && transicion.nuevo_estado === 'CANCELADO') {
      setCancelModal({ open: true, motivo: '', error: '' })
      return
    }

    transicionMutation.mutate(
      {
        pedidoId: pedido.id,
        data: { nuevo_estado: transicion.nuevo_estado },
      },
      {
        onSuccess: () => {
          onClose() // Close modal after transition
        },
      }
    )
  }

  const handleConfirmCancel = () => {
    if (!cancelModal.motivo.trim()) {
      setCancelModal((prev) => ({ ...prev, error: 'El motivo es obligatorio' }))
      return
    }

    cancelarMutation.mutate(
      {
        pedidoId: pedido.id,
        motivo: cancelModal.motivo,
      },
      {
        onSuccess: () => {
          setCancelModal({ open: false, motivo: '', error: '' })
          onClose()
        },
      }
    )
  }

  const tabs: { id: TabType; label: string }[] = [
    { id: 'resumen', label: 'Resumen' },
    { id: 'lineas', label: 'Líneas' },
    { id: 'historial', label: 'Historial' },
    { id: 'pago', label: 'Pago' },
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'resumen':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-500 dark:text-gray-400">ID</span>
                <p className="font-medium">#{pedido.id}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500 dark:text-gray-400">Estado</span>
                <p>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      ESTADO_COLORS[pedido.estado_codigo as EstadoPedido]
                    }`}
                  >
                    {ESTADO_LABELS[pedido.estado_codigo as EstadoPedido]}
                  </span>
                </p>
              </div>
              {pedido.cliente && (
                <div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">Cliente</span>
                  <p className="font-medium">
                    {pedido.cliente.nombre || ''} ({pedido.cliente.email})
                  </p>
                </div>
              )}
              <div>
                <span className="text-sm text-gray-500 dark:text-gray-400">Total</span>
                <p className="font-medium">{formatPrice(pedido.total)}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500 dark:text-gray-400">Costo envío</span>
                <p className="font-medium">{formatPrice(pedido.costo_envio)}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500 dark:text-gray-400">Forma de pago</span>
                <p className="font-medium">{pedido.forma_pago_codigo}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500 dark:text-gray-400">Fecha</span>
                <p className="font-medium">{formatDate(pedido.created_at)}</p>
              </div>
              {pedido.direccion_id && (
                <div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">Dirección ID</span>
                  <p className="font-medium">#{pedido.direccion_id}</p>
                </div>
              )}
            </div>
            {pedido.notas && (
              <div>
                <span className="text-sm text-gray-500 dark:text-gray-400">Notas</span>
                <p className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded">
                  {pedido.notas}
                </p>
              </div>
            )}
          </div>
        )

      case 'lineas':
        return (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-3 py-2 text-left">Producto</th>
                  <th className="px-3 py-2 text-right">Cantidad</th>
                  <th className="px-3 py-2 text-right">Precio</th>
                  <th className="px-3 py-2 text-right">Subtotal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                {pedido.detalles.map((detalle) => (
                  <tr key={detalle.id}>
                    <td className="px-3 py-2">
                      <div className="font-medium">{detalle.nombre_snapshot}</div>
                      {detalle.personalizacion && detalle.personalizacion.length > 0 && (
                        <div className="text-xs text-gray-500">
                          Sin: {detalle.personalizacion.join(', ')}
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-2 text-right">{detalle.cantidad}</td>
                    <td className="px-3 py-2 text-right">
                      {formatPrice(detalle.precio_snapshot)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {formatPrice(detalle.precio_snapshot * detalle.cantidad)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )

      case 'historial':
        return <HistorialTimeline historial={pedido.historial} />

      case 'pago':
        return (
          <div className="space-y-4">
            <div>
              <span className="text-sm text-gray-500 dark:text-gray-400">Método de pago</span>
              <p className="font-medium">{pedido.forma_pago_codigo}</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg text-center">
              <p className="text-gray-500 dark:text-gray-400">
                Información de pago del servidor no disponible en este change
              </p>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <>
      <Modal
        open={open}
        onClose={onClose}
        title={`Pedido #${pedido.id}`}
        size="lg"
        actions={
          <>
            <Button variant="outline" onClick={onClose}>
              Cerrar
            </Button>
            {transiciones.map((t, idx) => (
              <Button
                key={idx}
                variant={t.nuevo_estado === 'CANCELADO' ? 'danger' : 'primary'}
                onClick={() => handleTransicion(t)}
                disabled={transicionMutation.isPending || cancelarMutation.isPending}
              >
                {t.label}
              </Button>
            ))}
          </>
        }
      >
        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="min-h-[300px]">{renderTabContent()}</div>
      </Modal>

      {/* Cancel modal */}
      <Modal
        open={cancelModal.open}
        onClose={() => setCancelModal({ open: false, motivo: '', error: '' })}
        title="Cancelar Pedido"
        actions={
          <>
            <Button
              variant="outline"
              onClick={() => setCancelModal({ open: false, motivo: '', error: '' })}
            >
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
            ¿Estás seguro de que deseas cancelar el pedido #{pedido.id}?
          </p>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Motivo de cancelación <span className="text-red-500">*</span>
            </label>
            <textarea
              value={cancelModal.motivo}
              onChange={(e) =>
                setCancelModal((prev) => ({ ...prev, motivo: e.target.value, error: '' }))
              }
              placeholder="Ingrese el motivo de la cancelación..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            {cancelModal.error && (
              <p className="text-red-500 text-sm mt-1">{cancelModal.error}</p>
            )}
          </div>
        </div>
      </Modal>
    </>
  )
}

export default OrderDetailModal