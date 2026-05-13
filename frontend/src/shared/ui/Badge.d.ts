/**
 * Badge component for displaying status labels and tags
 */
import React from 'react';
export interface BadgeProps {
    children: React.ReactNode;
    variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
    className?: string;
}
export declare const Badge: React.FC<BadgeProps>;
//# sourceMappingURL=Badge.d.ts.map