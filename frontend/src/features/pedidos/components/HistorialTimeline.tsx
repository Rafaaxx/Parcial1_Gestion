/**
 * HistorialTimeline - Visualización Timeline del historial de estados
 */

import React from 'react'
import { HistorialEstado, ESTADO_LABELS, EstadoPedido } from '../types'

interface HistorialTimelineProps {
  historial: HistorialEstado[]
}

export const HistorialTimeline: React.FC<HistorialTimelineProps> = ({ historial }) => {
  // Sort by date ascending (oldest first)
  const historialOrdenado = [...historial].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  )

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

  const getEstadoLabel = (estado: string) => {
    return ESTADO_LABELS[estado as EstadoPedido] || estado
  }

  // Mostrar mensaje si no hay historial
  if (historialOrdenado.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <span className="text-4xl block mb-2">📋</span>
        <p>Este pedido aún no tiene transiciones de estado</p>
      </div>
    )
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

      <div className="space-y-6">
        {historialOrdenado.map((item, index) => {
          const isInitial = item.estado_desde === null
          const isTerminal =
            item.estado_hacia === 'ENTREGADO' || item.estado_hacia === 'CANCELADO'

          return (
            <div key={item.id} className="relative flex items-start gap-4">
              {/* Timeline dot */}
              <div
                className={`relative z-10 flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  isTerminal
                    ? 'bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-200'
                    : 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-200'
                }`}
              >
                {index + 1}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 pt-1">
                <div className="flex items-center gap-2 flex-wrap">
                  {isInitial ? (
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Estado inicial: {getEstadoLabel(item.estado_hacia)}
                    </span>
                  ) : (
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {getEstadoLabel(item.estado_desde || '')} →{' '}
                      {getEstadoLabel(item.estado_hacia)}
                    </span>
                  )}

                  {isTerminal && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                      Terminal
                    </span>
                  )}
                </div>

                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {formatDate(item.created_at)}
                  {item.usuario_id && (
                    <span className="ml-2">
                      • Usuario ID: {item.usuario_id}
                    </span>
                  )}
                </div>

                {item.observacion && (
                  <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm text-gray-600 dark:text-gray-300">
                    {item.observacion}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default HistorialTimeline