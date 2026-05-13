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
import React from 'react';
interface CheckoutFormProps {
    /** Cart items to convert to order */
    items: Array<{
        productoId: number;
        cantidad: number;
        personalizacion: number[];
    }>;
    /** Called when payment is initiated (before redirect) */
    onPaymentStart?: () => void;
    /** Called when there's an error */
    onError?: (error: string) => void;
}
export declare const CheckoutForm: React.FC<CheckoutFormProps>;
export {};
//# sourceMappingURL=CheckoutForm.d.ts.map