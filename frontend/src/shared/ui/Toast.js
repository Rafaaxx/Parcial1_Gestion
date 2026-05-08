import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export const Toast = ({ type, message, onClose }) => {
    const typeStyles = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-white',
        info: 'bg-blue-500 text-white',
    };
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ⓘ',
    };
    return (_jsxs("div", { className: `${typeStyles[type]} rounded-lg shadow-lg p-4 flex items-center gap-3 min-w-[300px]`, children: [_jsx("span", { className: "font-bold text-lg", children: icons[type] }), _jsx("span", { className: "flex-1", children: message }), onClose && (_jsx("button", { onClick: onClose, className: "hover:opacity-80", children: _jsx("svg", { className: "w-5 h-5", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M6 18L18 6M6 6l12 12" }) }) }))] }));
};
//# sourceMappingURL=Toast.js.map