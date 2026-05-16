/**
 * MisPedidosEmpty - Estado vacío cuando el cliente no tiene pedidos
 */

import { useNavigate } from 'react-router-dom'
import { Button } from '@/shared/ui/Button'

export function MisPedidosEmpty() {
  const navigate = useNavigate()

  return (
    <div className="text-center py-12">
      <div className="mb-4">
        <svg
          className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
      </div>
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        No tenés pedidos todavía
      </h2>
      <p className="text-gray-500 dark:text-gray-400 mb-6">
        Cuando realices tu primer pedido, podrás verlo aquí
      </p>
      <Button onClick={() => navigate('/productos')}>
        Ver Catálogo de Productos
      </Button>
    </div>
  )
}

export default MisPedidosEmpty