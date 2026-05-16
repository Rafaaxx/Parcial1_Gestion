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

  // Create order + payment in one flow
  crearPedidoYPagar: (items: Array<{
    productoId: number
    cantidad: number
    personalizacion: number[]
  }>) => Promise<number>
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
        const token = localStorage.getItem('access_token')
        const headers: Record<string, string> = { 'Content-Type': 'application/json' }
        if (token) headers['Authorization'] = `Bearer ${token}`
        
        try {
          setProcessing(pedidoId)

          const response = await fetch('http://localhost:8000/api/v1/pagos/crear', {
            method: 'POST',
            headers,
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
        const token = localStorage.getItem('access_token')
        const headers: Record<string, string> = { 'Content-Type': 'application/json' }
        if (token) headers['Authorization'] = `Bearer ${token}`

        try {
          const response = await fetch(`http://localhost:8000/api/v1/pagos/${pedidoId}`, {
            headers,
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

      crearPedidoYPagar: async (items) => {
        const { setProcessing, setInitPoint, setError } = get()

        // Get auth token from localStorage
        const token = localStorage.getItem('access_token')
        const headers: Record<string, string> = { 'Content-Type': 'application/json' }
        if (token) headers['Authorization'] = `Bearer ${token}`
        
        try {
          setProcessing(0)

          // Step 1: Create the order
          const pedidoRequest = {
            items: items.map(item => ({
              producto_id: item.productoId,
              cantidad: item.cantidad,
              personalizacion: item.personalizacion || null,
            })),
            forma_pago_codigo: 'MERCADOPAGO',
          }

          console.log(pedidoRequest);
          

          const pedidoResponse = await fetch('http://localhost:8000/api/v1/pedidos', {
            method: 'POST',
            headers,
            body: JSON.stringify(pedidoRequest),
          })

          console.log(pedidoResponse);
          

          if (!pedidoResponse.ok) {
            const error = await pedidoResponse.json()
            throw new Error(error.detail || 'Error al crear el pedido')
          }

          const pedidoData = await pedidoResponse.json()
          const pedidoId = pedidoData.id

          setProcessing(pedidoId)

          // Step 2: Create the payment
          const pagoResponse = await fetch('http://localhost:8000/api/v1/pagos/crear', {
            method: 'POST',
            headers,
            body: JSON.stringify({ pedido_id: pedidoId }),
          })

          if (!pagoResponse.ok) {
            const error = await pagoResponse.json()
            throw new Error(error.detail || 'Error al crear el pago')
          }

          const pagoData = await pagoResponse.json()

          if (pagoData.init_point) {
            setInitPoint(pagoData.init_point)
            window.location.href = pagoData.init_point
          } else if (pagoData.mp_status === 'approved') {
            set({ status: 'approved', mpPaymentId: pagoData.mp_payment_id, pedidoId })
          } else {
            set({ status: 'processing', pedidoId })
          }

          return pedidoId
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Error desconocido'
          console.log(message);
          
          setError(message)
          throw error
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