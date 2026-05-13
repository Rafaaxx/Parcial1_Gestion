import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { ESTADO_LABELS } from '../types';
export const HistorialTimeline = ({ historial }) => {
    // Sort by date ascending (oldest first)
    const historialOrdenado = [...historial].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('es-AR', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };
    const getEstadoLabel = (estado) => {
        return ESTADO_LABELS[estado] || estado;
    };
    // Mostrar mensaje si no hay historial
    if (historialOrdenado.length === 0) {
        return (_jsxs("div", { className: "text-center py-8 text-gray-500 dark:text-gray-400", children: [_jsx("span", { className: "text-4xl block mb-2", children: "\uD83D\uDCCB" }), _jsx("p", { children: "Este pedido a\u00FAn no tiene transiciones de estado" })] }));
    }
    return (_jsxs("div", { className: "relative", children: [_jsx("div", { className: "absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" }), _jsx("div", { className: "space-y-6", children: historialOrdenado.map((item, index) => {
                    const isInitial = item.estado_desde === null;
                    const isTerminal = item.estado_hacia === 'ENTREGADO' || item.estado_hacia === 'CANCELADO';
                    return (_jsxs("div", { className: "relative flex items-start gap-4", children: [_jsx("div", { className: `relative z-10 flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${isTerminal
                                    ? 'bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-200'
                                    : 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-200'}`, children: index + 1 }), _jsxs("div", { className: "flex-1 min-w-0 pt-1", children: [_jsxs("div", { className: "flex items-center gap-2 flex-wrap", children: [isInitial ? (_jsxs("span", { className: "text-sm font-medium text-gray-900 dark:text-gray-100", children: ["Estado inicial: ", getEstadoLabel(item.estado_hacia)] })) : (_jsxs("span", { className: "text-sm font-medium text-gray-900 dark:text-gray-100", children: [getEstadoLabel(item.estado_desde || ''), " \u2192", ' ', getEstadoLabel(item.estado_hacia)] })), isTerminal && (_jsx("span", { className: "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200", children: "Terminal" }))] }), _jsxs("div", { className: "text-xs text-gray-500 dark:text-gray-400 mt-1", children: [formatDate(item.created_at), item.usuario_id && (_jsxs("span", { className: "ml-2", children: ["\u2022 Usuario ID: ", item.usuario_id] }))] }), item.observacion && (_jsx("div", { className: "mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm text-gray-600 dark:text-gray-300", children: item.observacion }))] })] }, item.id));
                }) })] }));
};
export default HistorialTimeline;
//# sourceMappingURL=HistorialTimeline.js.map