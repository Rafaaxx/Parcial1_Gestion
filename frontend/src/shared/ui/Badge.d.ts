/**
 * Badge component for displaying labels, roles, and status indicators
 * Supports multiple variants and sizes with consistent Tailwind styling
 */
import React from 'react';
export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'info';
    size?: 'sm' | 'md' | 'lg';
    children: React.ReactNode;
}
export declare const Badge: React.ForwardRefExoticComponent<BadgeProps & React.RefAttributes<HTMLSpanElement>>;
//# sourceMappingURL=Badge.d.ts.map