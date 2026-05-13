/**
 * PaymentStatus — displays payment result and allows status checking
 *
 * Shows:
 * - Success: green checkmark, order confirmed
 * - Pending: yellow clock, payment in progress
 * - Rejected: red X, payment failed
 * - Error: error message
 *
 * Can also poll for status updates if user returns from MP without redirect completing
 */

import React, { useEffect } from 'react'
import { usePaymentStore, PaymentStatus as PaymentStatusType } from '../stores/paymentStore'

interface PaymentStatusProps {
  /** URL params from MP redirect (status, merchant_order_id, payment_id) */
  mpParams?: URLSearchParams
  /** Called when payment is approved */
  onApproved?: () => void
  /** Called when payment fails */
  onFailed?: (message: string) => void
}

export const PaymentStatus: React.FC<PaymentStatusProps> = ({
  mpParams,
  onApproved,
  onFailed,
}) => {
  const {
    status,
    pedidoId,
    errorMessage,
    checkPaymentStatus,
    reset,
  } = usePaymentStore()

  // Check status when component mounts or params change
  useEffect(() => {
    if (pedidoId && status === 'idle') {
      // User returned from MP, check current status
      checkPaymentStatus(pedidoId)
    }
  }, [pedidoId, status, checkPaymentStatus])

  // Handle MP redirect params
  useEffect(() => {
    if (mpParams) {
      const mpStatus = mpParams.get('status')
      const collectionStatus = mpParams.get('collection_status')

      if (mpStatus === 'approved' || collectionStatus === 'approved') {
        onApproved?.()
      } else if (mpStatus === 'rejected' || collectionStatus === 'rejected') {
        onFailed?.('Pago rechazado por MercadoPago')
      }
    }
  }, [mpParams, onApproved, onFailed])

  const handleRetry = () => {
    reset()
  }

  const renderContent = () => {
    switch (status) {
      case 'processing':
        return (
          <div className="text-center py-8">
            <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Procesando pago...
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Tu pago está siendo procesado. Por favor espera.
            </p>
          </div>
        )

      case 'approved':
        return (
          <div className="text-center py-8">
            <div className="h-12 w-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="h-8 w-8 text-green-600 dark:text-green-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              ¡Pago aprobado!
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Tu pedido ha sido confirmado y está en proceso de preparación.
            </p>
          </div>
        )

      case 'rejected':
        return (
          <div className="text-center py-8">
            <div className="h-12 w-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="h-8 w-8 text-red-600 dark:text-red-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Pago rechazado
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {errorMessage || 'Tu pago fue rechazado por MercadoPago.'}
            </p>
            <button
              onClick={handleRetry}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
            >
              Intentar de nuevo
            </button>
          </div>
        )

      case 'error':
        return (
          <div className="text-center py-8">
            <div className="h-12 w-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="h-8 w-8 text-yellow-600 dark:text-yellow-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Error en el pago
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {errorMessage || 'Ocurrió un error al procesar tu pago.'}
            </p>
            <button
              onClick={handleRetry}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
            >
              Reintentar
            </button>
          </div>
        )

      default: // idle
        return null
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      {renderContent()}
    </div>
  )
}