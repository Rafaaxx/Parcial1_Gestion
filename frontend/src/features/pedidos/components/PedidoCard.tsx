/**
 * PedidoCard - Tarjeta resumen de un pedido para el listado de Mis Pedidos
 */

import { useNavigate } from 'react-router-dom'
import { PedidoListItem, ESTADO_LABELS, ESTADO_COLORS, EstadoPedido } from '../types'
import { Button } from '@/shared/ui/Button'

interface PedidoCardProps {
  pedido: PedidoListItem
}

export function PedidoCard({ pedido }: PedidoCardProps) {
  const navigate = useNavigate()

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('es-AR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(amount)
  }

  const estadoColor = ESTADO_COLORS[pedido.estado_codigo as EstadoPedido] || 'bg-gray-100 text-gray-800'
  const estadoLabel = ESTADO_LABELS[pedido.estado_codigo as EstadoPedido] || pedido.estado_codigo

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Pedido #{pedido.id}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {formatDate(pedido.created_at)}
          </p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${estadoColor}`}>
          {estadoLabel}
        </span>
      </div>

      <div className="flex justify-between items-center mt-4">
        <div className="text-right">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total</p>
          <p className="text-xl font-bold text-gray-900 dark:text-white">
            {formatCurrency(pedido.total)}
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() => navigate(`/mis-pedidos/${pedido.id}`)}
        >
          Ver Detalle
        </Button>
      </div>
    </div>
  )
}