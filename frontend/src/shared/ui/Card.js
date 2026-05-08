import { jsx as _jsx } from "react/jsx-runtime";
/**
 * Card component for content containers
 */
import React from 'react';
export const Card = React.forwardRef(({ className = '', interactive = false, children, ...props }, ref) => {
    const hoverStyles = interactive ? 'hover:shadow-lg transition-shadow' : '';
    return (_jsx("div", { ref: ref, className: `card-base p-4 ${hoverStyles} ${className}`, ...props, children: children }));
});
Card.displayName = 'Card';
//# sourceMappingURL=Card.js.map