/**
 * PedidoDetailTabs - Componente de tabs para el detalle del pedido
 * Tabs: Resumen | Líneas | Historial | Pago
 */

import { useState } from 'react'
import { Pedido, HistorialEstado, ESTADO_LABELS, EstadoPedido, ESTADO_COLORS } from '../types'
import { HistorialTimeline } from './HistorialTimeline'
import { PaymentStatusBadge } from './PaymentStatusBadge'
import { PaymentStatus } from '../api'

type TabType = 'resumen' | 'lineas' | 'historial' | 'pago'

interface PedidoDetailTabsProps {
  pedido: Pedido
  historial?: HistorialEstado[]
  paymentStatus?: string | null
}

export function PedidoDetailTabs({ pedido, historial = [], paymentStatus }: PedidoDetailTabsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('resumen')

  const tabs: { id: TabType; label: string }[] = [
    { id: 'resumen', label: 'Resumen' },
    { id: 'lineas', label: 'Líneas' },
    { id: 'historial', label: 'Historial' },
    { id: 'pago', label: 'Pago' },
  ]

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('es-AR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const estadoColor = ESTADO_COLORS[pedido.estado_codigo as EstadoPedido] || 'bg-gray-100'
  const estadoLabel = ESTADO_LABELS[pedido.estado_codigo as EstadoPedido] || pedido.estado_codigo

  const renderTabContent = () => {
    switch (activeTab) {
      case 'resumen':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">ID del Pedido</p>
                <p className="font-medium text-gray-900 dark:text-white">#{pedido.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Estado</p>
                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${estadoColor}`}>
                  {estadoLabel}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Fecha de Creación</p>
                <p className="font-medium text-gray-900 dark:text-white">{formatDate(pedido.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Forma de Pago</p>
                <p className="font-medium text-gray-900 dark:text-white">
                  {pedido.forma_pago_codigo === 'MP' ? 'MercadoPago' : pedido.forma_pago_codigo}
                </p>
              </div>
            </div>

            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <div className="flex justify-between mb-2">
                <span className="text-gray-600 dark:text-gray-400">Subtotal</span>
                <span className="text-gray-900 dark:text-white">{formatCurrency(pedido.total - pedido.costo_envio)}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-600 dark:text-gray-400">Costo de envío</span>
                <span className="text-gray-900 dark:text-white">{formatCurrency(pedido.costo_envio)}</span>
              </div>
              <div className="flex justify-between font-bold text-lg border-t border-gray-200 dark:border-gray-700 pt-2">
                <span>Total</span>
                <span>{formatCurrency(pedido.total)}</span>
              </div>
            </div>

            {pedido.notas && (
              <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">Notas</p>
                <p className="text-gray-900 dark:text-white">{pedido.notas}</p>
              </div>
            )}
          </div>
        )

      case 'lineas':
        return (
          <div className="space-y-3">
            {pedido.detalles && pedido.detalles.length > 0 ? (
              pedido.detalles.map((detalle) => (
                <div
                  key={detalle.id}
                  className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{detalle.nombre_snapshot}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Cantidad: {detalle.cantidad}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(detalle.precio_snapshot * detalle.cantidad)}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(detalle.precio_snapshot)} c/u
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 dark:text-gray-400">No hay detalles del pedido</p>
            )}
          </div>
        )

      case 'historial':
        return historial && historial.length > 0 ? (
          <HistorialTimeline historial={historial} />
        ) : (
          <p className="text-gray-500 dark:text-gray-400">No hay historial de estados</p>
        )

      case 'pago':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <p className="text-gray-600 dark:text-gray-400">Estado del Pago:</p>
              <PaymentStatusBadge status={paymentStatus ?? null} />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              El estado del pago se actualiza automáticamente cuando MercadoPago notifica al sistema.
            </p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div>
      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors relative ${
              activeTab === tab.id
                ? 'text-blue-600 dark:text-blue-400'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            {tab.label}
            {activeTab === tab.id && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400" />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="py-2">{renderTabContent()}</div>
    </div>
  )
}