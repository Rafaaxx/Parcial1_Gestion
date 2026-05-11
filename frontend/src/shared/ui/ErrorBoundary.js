import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ErrorBoundary component to catch and display React errors gracefully
 */
import React from 'react';
export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        Object.defineProperty(this, "handleRetry", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: () => {
                this.setState({ hasError: false, error: null });
            }
        });
        this.state = { hasError: false, error: null };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error('[ErrorBoundary] Caught error:', error, errorInfo);
    }
    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }
            return (_jsx("div", { className: "min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 p-4", children: _jsxs("div", { className: "max-w-lg w-full bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-red-200 dark:border-red-800 p-8", children: [_jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsx("span", { className: "text-4xl", children: "\u26A0\uFE0F" }), _jsx("h2", { className: "text-xl font-bold text-gray-900 dark:text-gray-50", children: "Algo sali\u00F3 mal" })] }), _jsx("p", { className: "text-gray-600 dark:text-gray-400 mb-4", children: "Ocurri\u00F3 un error inesperado. Puede intentar recuperar la aplicaci\u00F3n o contactar al soporte." }), import.meta.env.DEV && this.state.error && (_jsxs("div", { className: "mb-6 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800", children: [_jsxs("p", { className: "text-sm font-mono text-red-700 dark:text-red-300 mb-2", children: [this.state.error.name, ": ", this.state.error.message] }), this.state.error.stack && (_jsx("pre", { className: "text-xs font-mono text-red-600 dark:text-red-400 overflow-auto max-h-48 whitespace-pre-wrap", children: this.state.error.stack }))] })), _jsx("button", { onClick: this.handleRetry, className: "px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors", children: "Reintentar" })] }) }));
        }
        return this.props.children;
    }
}
export default ErrorBoundary;
//# sourceMappingURL=ErrorBoundary.js.map