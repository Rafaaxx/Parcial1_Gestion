/**
 * CheckoutForm — payment initiation component
 *
 * This component:
 * 1. Shows "Pagar con MercadoPago" button
 * 2. Creates order + payment in one flow (crearPedidoYPagar)
 * 3. Redirects to MP checkout (init_point)
 *
 * Note: We use checkout redirection, not direct card tokenization.
 * This is simpler and more common for this use case.
 */

import React, { useEffect } from 'react'
import { usePaymentStore } from '../stores/paymentStore'

interface CheckoutFormProps {
  /** Cart items to convert to order */
  items: Array<{
    productoId: number
    cantidad: number
    personalizacion: number[]
  }>
  /** Called when payment is initiated (before redirect) */
  onPaymentStart?: () => void
  /** Called when there's an error */
  onError?: (error: string) => void
}

export const CheckoutForm: React.FC<CheckoutFormProps> = ({
  items,
  onPaymentStart,
  onError,
}) => {
  const { crearPedidoYPagar, status, errorMessage, initPoint, reset } = usePaymentStore()

  // 3. Agrega este useEffect para limpiar estados colgados al montar el componente
  useEffect(() => {
    // Si el usuario llega a esta pantalla y por algún motivo el store
    // había quedado guardado como "processing" o "error", lo limpiamos.
    if (status !== 'idle') {
      reset()
    }
  }, [reset, status])

  console.log('CheckoutForm render - status:', status, 'errorMessage:', errorMessage, 'initPoint:', initPoint)

  const isLoading = status === 'processing'
  const isDisabled = items.length === 0

  const handlePayment = async () => {
    if (items.length === 0) {
      onError?.('El carrito está vacío')
      return
    }

    try {
      onPaymentStart?.()
      await crearPedidoYPagar(items)
      // Redirect happens inside crearPedidoYPagar
    } catch (error) {
      console.log(error);
      
      const message = error instanceof Error ? error.message : 'Error al iniciar pago'
      onError?.(message)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Finalizar Compra
      </h3>

      <div className="space-y-4">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Serás redirigido a MercadoPago para completar el pago de forma segura.
        </p>

        {errorMessage && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3">
            <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p>
          </div>
        )}

        <button
          onClick={handlePayment}
          disabled={isLoading || isDisabled}
          className={`
            w-full py-3 px-4 rounded-lg font-medium transition-colors
            flex items-center justify-center gap-2
            ${
              isLoading || isDisabled
                ? 'bg-gray-400 dark:bg-gray-600 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }
          `}
        >
          {isLoading ? (
            <>
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Procesando...
            </>
          ) : (
            <>
              <svg
                className="w-5 h-5"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
              </svg>
              Pagar con MercadoPago
            </>
          )}
        </button>

        <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
          Tus datos de tarjeta son procesados de forma segura por MercadoPago.
          Nosotros nunca vemos ni almacenamos tu información de pago.
        </p>
      </div>
    </div>
  )
}