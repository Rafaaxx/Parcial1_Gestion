/**
 * ToastNotifier — simple state-based toast notification system
 *
 * No external library. Renders a fixed-position toast container at top-right.
 * Usage: wrap your app or use the hook to show toasts from any component.
 */
import React from 'react';
export interface ToastMessage {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
}
interface ToastNotifierContextValue {
    showToast: (type: ToastMessage['type'], message: string) => void;
}
export declare function useToast(): ToastNotifierContextValue;
export declare const ToastNotifierProvider: React.FC<{
    children: React.ReactNode;
}>;
export default ToastNotifierProvider;
//# sourceMappingURL=ToastNotifier.d.ts.map