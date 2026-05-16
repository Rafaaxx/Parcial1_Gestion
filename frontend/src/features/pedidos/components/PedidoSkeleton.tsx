/**
 * PedidoSkeleton - Skeleton loader para el listado de pedidos
 */

import { Skeleton } from '@/shared/ui/Skeleton'

export function PedidoSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
      <div className="flex justify-between items-start mb-3">
        <div>
          <Skeleton className="h-6 w-24 mb-2" />
          <Skeleton className="h-4 w-40" />
        </div>
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>

      <div className="flex justify-between items-center mt-4">
        <div>
          <Skeleton className="h-4 w-12 mb-1" />
          <Skeleton className="h-7 w-24" />
        </div>
        <Skeleton className="h-9 w-28" />
      </div>
    </div>
  )
}

export function PedidosListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <PedidoSkeleton key={i} />
      ))}
    </div>
  )
}