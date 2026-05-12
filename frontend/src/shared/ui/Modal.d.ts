/**
 * Modal dialog component
 */
import React from 'react';
export interface ModalAction {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary' | 'danger';
}
export interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    actions?: ModalAction[];
    children?: React.ReactNode;
}
export declare const Modal: React.FC<ModalProps>;
//# sourceMappingURL=modal.d.ts.map