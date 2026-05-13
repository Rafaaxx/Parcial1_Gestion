import { jsx as _jsx } from "react/jsx-runtime";
const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
};
export const Spinner = ({ size = 'md', className = '', }) => {
    return (_jsx("div", { "data-testid": "loading-spinner", className: `animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 ${sizeClasses[size]} ${className}` }));
};
export default Spinner;
//# sourceMappingURL=Spinner.js.map