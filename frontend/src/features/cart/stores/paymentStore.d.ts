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
export type PaymentStatus = 'idle' | 'processing' | 'approved' | 'rejected' | 'error';
interface PaymentState {
    status: PaymentStatus;
    pedidoId: number | null;
    mpPaymentId: number | null;
    initPoint: string | null;
    errorMessage: string | null;
    setProcessing: (pedidoId: number) => void;
    setInitPoint: (initPoint: string) => void;
    setApproved: (mpPaymentId: number) => void;
    setRejected: (errorMessage?: string) => void;
    setError: (message: string) => void;
    reset: () => void;
    createPayment: (pedidoId: number) => Promise<void>;
    checkPaymentStatus: (pedidoId: number) => Promise<void>;
    crearPedidoYPagar: (items: Array<{
        productoId: number;
        cantidad: number;
        personalizacion: number[];
    }>) => Promise<number>;
}
export declare const usePaymentStore: import("zustand").UseBoundStore<Omit<import("zustand").StoreApi<PaymentState>, "persist"> & {
    persist: {
        setOptions: (options: Partial<import("zustand/middleware").PersistOptions<PaymentState, {
            status: PaymentStatus;
            pedidoId: number | null;
            mpPaymentId: number | null;
        }>>) => void;
        clearStorage: () => void;
        rehydrate: () => Promise<void> | void;
        hasHydrated: () => boolean;
        onHydrate: (fn: (state: PaymentState) => void) => () => void;
        onFinishHydration: (fn: (state: PaymentState) => void) => () => void;
        getOptions: () => Partial<import("zustand/middleware").PersistOptions<PaymentState, {
            status: PaymentStatus;
            pedidoId: number | null;
            mpPaymentId: number | null;
        }>>;
    };
}>;
export declare const selectPaymentStatus: (state: PaymentState) => PaymentStatus;
export declare const selectIsProcessing: (state: PaymentState) => boolean;
export declare const selectIsApproved: (state: PaymentState) => boolean;
export declare const selectIsRejected: (state: PaymentState) => boolean;
export declare const selectHasError: (state: PaymentState) => boolean;
export declare const selectErrorMessage: (state: PaymentState) => string | null;
export {};
//# sourceMappingURL=paymentStore.d.ts.map