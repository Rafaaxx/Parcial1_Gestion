import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Input component with label and validation
 */
import React from 'react';
export const Input = React.forwardRef(({ className = '', label, error, ...props }, ref) => {
    return (_jsxs("div", { className: "flex flex-col gap-1", children: [label && _jsx("label", { className: "text-sm font-medium text-gray-700 dark:text-gray-300", children: label }), _jsx("input", { ref: ref, className: `
            px-3 py-2 border rounded-md transition-colors
            bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-50
            border-gray-300 dark:border-gray-700
            hover:border-gray-400 dark:hover:border-gray-600
            focus:outline-none focus:ring-2 focus:ring-sky-500
            disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed
            ${error ? 'border-red-500 focus:ring-red-500' : ''}
            ${className}
          `, ...props }), error && _jsx("span", { className: "text-sm text-red-500", children: error })] }));
});
Input.displayName = 'Input';
//# sourceMappingURL=Input.js.map