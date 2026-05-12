import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ToastNotifier — simple state-based toast notification system
 *
 * No external library. Renders a fixed-position toast container at top-right.
 * Usage: wrap your app or use the hook to show toasts from any component.
 */
import React, { useState, useCallback, useRef, useEffect } from 'react';
const ToastNotifierContext = React.createContext(null);
let toastIdCounter = 0;
export function useToast() {
    const ctx = React.useContext(ToastNotifierContext);
    if (!ctx) {
        // Fallback: return a no-op if used outside provider (avoids crashes during development)
        return { showToast: () => { } };
    }
    return ctx;
}
export const ToastNotifierProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);
    const timersRef = useRef(new Map());
    const removeToast = useCallback((id) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
        const timer = timersRef.current.get(id);
        if (timer) {
            clearTimeout(timer);
            timersRef.current.delete(id);
        }
    }, []);
    const showToast = useCallback((type, message) => {
        const id = `toast-${++toastIdCounter}`;
        const newToast = { id, type, message };
        setToasts((prev) => [...prev, newToast]);
        // Auto-dismiss after 3 seconds
        const timer = setTimeout(() => removeToast(id), 3000);
        timersRef.current.set(id, timer);
    }, [removeToast]);
    // Cleanup all timers on unmount
    useEffect(() => {
        return () => {
            timersRef.current.forEach((timer) => clearTimeout(timer));
            timersRef.current.clear();
        };
    }, []);
    const typeStyles = {
        success: 'bg-green-600 text-white',
        error: 'bg-red-600 text-white',
        warning: 'bg-yellow-500 text-white',
        info: 'bg-blue-600 text-white',
    };
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ⓘ',
    };
    return (_jsxs(ToastNotifierContext.Provider, { value: { showToast }, children: [children, _jsx("div", { className: "fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none", children: toasts.map((toast) => (_jsxs("div", { className: `${typeStyles[toast.type]} rounded-lg shadow-lg px-4 py-3 flex items-center gap-3 min-w-[280px] max-w-[400px] pointer-events-auto animate-slide-in-right`, role: "alert", children: [_jsx("span", { className: "font-bold text-lg flex-shrink-0", children: icons[toast.type] }), _jsx("span", { className: "flex-1 text-sm font-medium", children: toast.message }), _jsx("button", { onClick: () => removeToast(toast.id), className: "flex-shrink-0 hover:opacity-80", "aria-label": "Cerrar", children: _jsx("svg", { className: "w-4 h-4", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M6 18L18 6M6 6l12 12" }) }) })] }, toast.id))) })] }));
};
export default ToastNotifierProvider;
//# sourceMappingURL=ToastNotifier.js.map