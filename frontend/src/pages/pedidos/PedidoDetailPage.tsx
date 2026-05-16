/**
 * PedidoDetailPage - Página de detalle de un pedido específico
 * GET /mis-pedidos/:pedidoId
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { usePedidoDetail, usePedidoHistorial, usePedidoPago, useCancelarPedido } from '@/features/pedidos/hooks'
import { PedidoDetailTabs, CancelarPedidoModal } from '@/features/pedidos/components'
import { Button } from '@/shared/ui/Button'
import { Skeleton } from '@/shared/ui/Skeleton'
import { esEstadoTerminal } from '@/features/pedidos/types'

export function PedidoDetailPage() {
  const { pedidoId } = useParams<{ pedidoId: string }>()
  const navigate = useNavigate()
  const id = Number(pedidoId)

  const [showCancelModal, setShowCancelModal] = useState(false)

  const { data: pedido, isLoading: isLoadingPedido, error: errorPedido } = usePedidoDetail(id)
  const { data: historial, isLoading: isLoadingHistorial } = usePedidoHistorial(id)
  const { data: pago } = usePedidoPago(id)

  const cancelarMutation = useCancelarPedido()

  useEffect(() => {
    // Scroll to top on mount
    window.scrollTo(0, 0)
  }, [])

  const handleCancelar = async (motivo: string) => {
    try {
      await cancelarMutation.mutateAsync({ pedidoId: id, motivo })
      setShowCancelModal(false)
      // Show success and redirect - will be handled by toast system
      navigate('/mis-pedidos')
    } catch (error) {
      // Error is handled by the mutation
      console.error('Error canceling order:', error)
    }
  }

  if (isLoadingPedido) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Button variant="secondary" onClick={() => navigate('/mis-pedidos')} className="mb-4">
          ← Volver a Mis Pedidos
        </Button>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <Skeleton className="h-8 w-48 mb-4" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4 mb-2" />
          <Skeleton className="h-4 w-1/2 mb-4" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  if (errorPedido) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Button variant="secondary" onClick={() => navigate('/mis-pedidos')} className="mb-4">
          ← Volver a Mis Pedidos
        </Button>
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
            Error al cargar el pedido
          </h2>
          <p className="text-red-600 dark:text-red-300">{errorPedido.message}</p>
        </div>
      </div>
    )
  }

  if (!pedido) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Button variant="secondary" onClick={() => navigate('/mis-pedidos')} className="mb-4">
          ← Volver a Mis Pedidos
        </Button>
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200">
            Pedido no encontrado
          </h2>
        </div>
      </div>
    )
  }

  const canCancelar = pedido.estado_codigo === 'PENDIENTE'

  return (
    <div className="container mx-auto px-4 py-8">
      <Button variant="secondary" onClick={() => navigate('/mis-pedidos')} className="mb-4">
        ← Volver a Mis Pedidos
      </Button>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Detalle del Pedido #{pedido.id}
            </h1>
          </div>
          {canCancelar && (
            <Button
              variant="danger"
              onClick={() => setShowCancelModal(true)}
            >
              Cancelar Pedido
            </Button>
          )}
        </div>

        <PedidoDetailTabs
          pedido={pedido}
          historial={historial}
          paymentStatus={pago?.mp_status}
        />
      </div>

      <CancelarPedidoModal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        onConfirm={handleCancelar}
        isLoading={cancelarMutation.isPending}
      />
    </div>
  )
}

export default PedidoDetailPage