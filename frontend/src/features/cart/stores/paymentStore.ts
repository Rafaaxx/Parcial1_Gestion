/**
 * Payment store — Zustand store for MercadoPago payment flow
 *
 * States:
 * - idle: No payment initiated
 * - processing: Payment being created or processed
 * - approved: Payment approved
 * - rejected: Payment rejected
 * - error: Error occurred
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type PaymentStatus = 'idle' | 'processing' | 'approved' | 'rejected' | 'error'

interface PaymentState {
  // State
  status: PaymentStatus
  pedidoId: number | null
  mpPaymentId: number | null
  initPoint: string | null
  errorMessage: string | null

  // Actions
  setProcessing: (pedidoId: number) => void
  setInitPoint: (initPoint: string) => void
  setApproved: (mpPaymentId: number) => void
  setRejected: (errorMessage?: string) => void
  setError: (message: string) => void
  reset: () => void

  // Async actions (call API)
  createPayment: (pedidoId: number) => Promise<void>
  checkPaymentStatus: (pedidoId: number) => Promise<void>
}

export const usePaymentStore = create<PaymentState>()(
  persist(
    (set, get) => ({
      // Initial state
      status: 'idle',
      pedidoId: null,
      mpPaymentId: null,
      initPoint: null,
      errorMessage: null,

      setProcessing: (pedidoId: number) => set({
        status: 'processing',
        pedidoId,
        mpPaymentId: null,
        initPoint: null,
        errorMessage: null,
      }),

      setInitPoint: (initPoint: string) => set({
        initPoint,
        status: 'processing', // Still processing until user completes on MP
      }),

      setApproved: (mpPaymentId: number) => set({
        status: 'approved',
        mpPaymentId,
        errorMessage: null,
      }),

      setRejected: (errorMessage = 'Pago rechazado') => set({
        status: 'rejected',
        errorMessage,
      }),

      setError: (message: string) => set({
        status: 'error',
        errorMessage: message,
      }),

      reset: () => set({
        status: 'idle',
        pedidoId: null,
        mpPaymentId: null,
        initPoint: null,
        errorMessage: null,
      }),

      createPayment: async (pedidoId: number) => {
        const { setProcessing, setInitPoint, setError } = get()

        try {
          setProcessing(pedidoId)

          const response = await fetch('/api/v1/pagos/crear', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              // Add auth header - assume token is available
            },
            body: JSON.stringify({ pedido_id: pedidoId }),
          })

          if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Error al crear pago')
          }

          const data = await response.json()

          if (data.init_point) {
            // Redirect checkout - store the URL
            setInitPoint(data.init_point)
            // Redirect to MP
            window.location.href = data.init_point
          } else if (data.status === 'approved') {
            // Direct approval (rare for checkout redirect)
            set({ status: 'approved', mpPaymentId: data.mp_payment_id })
          } else {
            // Other status - keep processing
            set({ status: 'processing' })
          }
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Error desconocido'
          setError(message)
          throw error
        }
      },

      checkPaymentStatus: async (pedidoId: number) => {
        const { setApproved, setRejected, setError } = get()

        try {
          const response = await fetch(`/api/v1/pagos/${pedidoId}`, {
            headers: {
              // Add auth header
            },
          })

          if (!response.ok) {
            if (response.status === 404) {
              // No payment yet
              return
            }
            throw new Error('Error al consultar pago')
          }

          const data = await response.json()

          switch (data.mp_status) {
            case 'approved':
              setApproved(data.mp_payment_id)
              break
            case 'rejected':
              setRejected(data.mp_status_detail || 'Pago rechazado')
              break
            case 'pending':
            case 'in_process':
              set({ status: 'processing' })
              break
            default:
              setError(`Estado desconocido: ${data.mp_status}`)
          }
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Error desconocido'
          setError(message)
        }
      },
    }),
    {
      name: 'payment-store',
      partialize: (state) => ({
        // Only persist these fields
        status: state.status,
        pedidoId: state.pedidoId,
        mpPaymentId: state.mpPaymentId,
      }),
    }
  )
)

// Selectors
export const selectPaymentStatus = (state: PaymentState) => state.status
export const selectIsProcessing = (state: PaymentState) => state.status === 'processing'
export const selectIsApproved = (state: PaymentState) => state.status === 'approved'
export const selectIsRejected = (state: PaymentState) => state.status === 'rejected'
export const selectHasError = (state: PaymentState) => state.status === 'error'
export const selectErrorMessage = (state: PaymentState) => state.errorMessage