/**
 * MisPedidosPage - Página principal del cliente para ver sus pedidos
 * GET /mis-pedidos
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePedidos } from '@/features/pedidos/hooks'
import { PedidoCard, PedidosListSkeleton } from '@/features/pedidos/components'
import { MisPedidosEmpty } from './MisPedidosEmpty'
import { Select } from '@/shared/ui/Select'
import { Button } from '@/shared/ui/Button'
import { ESTADOS_TERMINALES } from '@/features/pedidos/types'

const ESTADOS_OPCIONES = [
  { value: '', label: 'Todos los estados' },
  { value: 'PENDIENTE', label: 'Pendiente' },
  { value: 'CONFIRMADO', label: 'Confirmado' },
  { value: 'EN_PREP', label: 'En Preparación' },
  { value: 'EN_CAMINO', label: 'En Camino' },
  { value: 'ENTREGADO', label: 'Entregado' },
  { value: 'CANCELADO', label: 'Cancelado' },
]

export function MisPedidosPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(0)
  const [estadoFilter, setEstadoFilter] = useState('')
  const limit = 10

  const { data, isLoading, error } = usePedidos(page * limit, limit, {
    estado: estadoFilter || undefined,
    solo_mios: true,  // Force to show only my orders (ignores ADMIN role)
  })

  const totalPages = data ? Math.ceil(data.total / limit) : 0

  const handlePrevious = () => {
    if (page > 0) setPage(page - 1)
  }

  const handleNext = () => {
    if (data && page < totalPages - 1) setPage(page + 1)
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
            Error al cargar pedidos
          </h2>
          <p className="text-red-600 dark:text-red-300">{error.message}</p>
          <Button
            variant="secondary"
            onClick={() => window.location.reload()}
            className="mt-4"
          >
            Reintentar
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Mis Pedidos
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Consultá el historial de tus pedidos y su estado
        </p>
      </div>

      {/* Filtro por estado */}
      <div className="mb-6">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Filtrar por estado:
          </label>
          <div className="w-64">
            <Select
              value={estadoFilter}
              onChange={(e) => {
                setEstadoFilter(e.target.value)
                setPage(0)
              }}
              options={ESTADOS_OPCIONES}
            />
          </div>
        </div>
      </div>

      {/* Loading skeleton */}
      {isLoading && <PedidosListSkeleton count={5} />}

      {/* Lista de pedidos */}
      {!isLoading && data && (
        <>
          {data.items.length === 0 ? (
            <MisPedidosEmpty />
          ) : (
            <div className="space-y-4">
              {data.items.map((pedido) => (
                <PedidoCard
                  key={pedido.id}
                  pedido={pedido}
                />
              ))}

              {/* Paginación */}
              {totalPages > 1 && (
                <div className="flex justify-center items-center gap-4 mt-6">
                  <Button
                    variant="secondary"
                    onClick={handlePrevious}
                    disabled={page === 0}
                  >
                    Anterior
                  </Button>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Página {page + 1} de {totalPages} ({data.total} pedidos)
                  </span>
                  <Button
                    variant="secondary"
                    onClick={handleNext}
                    disabled={!data || page >= totalPages - 1}
                  >
                    Siguiente
                  </Button>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default MisPedidosPage