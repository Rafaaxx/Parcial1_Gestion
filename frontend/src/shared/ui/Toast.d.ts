/**
 * Toast notification component
 */
import React from 'react';
export interface ToastProps {
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    onClose?: () => void;
}
export declare const Toast: React.FC<ToastProps>;
//# sourceMappingURL=Toast.d.ts.map