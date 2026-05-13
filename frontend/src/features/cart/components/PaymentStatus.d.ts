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
import React from 'react';
interface PaymentStatusProps {
    /** URL params from MP redirect (status, merchant_order_id, payment_id) */
    mpParams?: URLSearchParams;
    /** Called when payment is approved */
    onApproved?: () => void;
    /** Called when payment fails */
    onFailed?: (message: string) => void;
}
export declare const PaymentStatus: React.FC<PaymentStatusProps>;
export {};
//# sourceMappingURL=PaymentStatus.d.ts.map