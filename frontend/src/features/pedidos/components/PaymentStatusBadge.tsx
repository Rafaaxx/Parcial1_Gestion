/**
 * PaymentStatusBadge - Badge para mostrar el estado del pago
 */

import { PaymentStatus } from '../api'

interface PaymentStatusBadgeProps {
  status: PaymentStatus | string | null
}

const PAYMENT_STATUS_LABELS: Record<string, string> = {
  approved: 'Pagado',
  rejected: 'Rechazado',
  in_process: 'Procesando',
  pending: 'Pendiente',
}

const PAYMENT_STATUS_COLORS: Record<string, string> = {
  approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  in_process: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
}

export function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  if (!status || status === 'none') {
    return (
      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
        Sin información de pago
      </span>
    )
  }

  const label = PAYMENT_STATUS_LABELS[status] || status
  const color = PAYMENT_STATUS_COLORS[status] || 'bg-gray-100 text-gray-800'

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${color}`}>
      {label}
    </span>
  )
}