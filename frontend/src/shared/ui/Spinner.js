import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Spinner component for loading states
 * Displays an animated loading indicator with customizable size and color
 */
import React from 'react';
export const Spinner = React.forwardRef(({ className = '', size = 'md', color = 'primary', label, ...props }, ref) => {
    const sizeStyles = {
        sm: 'w-4 h-4',
        md: 'w-8 h-8',
        lg: 'w-12 h-12',
        xl: 'w-16 h-16',
    };
    const colorStyles = {
        primary: 'text-blue-600 dark:text-blue-400',
        secondary: 'text-gray-600 dark:text-gray-400',
        white: 'text-white',
        gray: 'text-gray-400 dark:text-gray-600',
    };
    return (_jsxs("div", { ref: ref, className: `flex flex-col items-center justify-center gap-3 ${className}`, ...props, children: [_jsxs("svg", { className: `animate-spin ${sizeStyles[size]} ${colorStyles[color]}`, fill: "none", viewBox: "0 0 24 24", xmlns: "http://www.w3.org/2000/svg", children: [_jsx("circle", { className: "opacity-25", cx: "12", cy: "12", r: "10", stroke: "currentColor", strokeWidth: "4" }), _jsx("path", { className: "opacity-75", fill: "currentColor", d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" })] }), label && (_jsx("p", { className: "text-sm font-medium text-gray-600 dark:text-gray-400", children: label }))] }));
});
Spinner.displayName = 'Spinner';
//# sourceMappingURL=Spinner.js.map