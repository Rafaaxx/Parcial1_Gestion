/**
 * Spinner component for loading states
 * Displays an animated loading indicator with customizable size and color
 */
import React from 'react';
export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
    size?: 'sm' | 'md' | 'lg' | 'xl';
    color?: 'primary' | 'secondary' | 'white' | 'gray';
    label?: string;
}
export declare const Spinner: React.ForwardRefExoticComponent<SpinnerProps & React.RefAttributes<HTMLDivElement>>;
//# sourceMappingURL=Spinner.d.ts.map