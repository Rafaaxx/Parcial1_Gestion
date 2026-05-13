import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * OrderDetailModal - Modal con tabs para ver detalle del pedido
 */
import { useState } from 'react';
import { Modal } from '@/shared/ui';
import { ESTADO_LABELS, ESTADO_COLORS } from '../types';
import { HistorialTimeline } from './HistorialTimeline';
import { getTransicionesDisponibles } from '../hooks';
import { useAuthStore } from '@/features/auth/store';
import { useTransicionEstado, useCancelarPedido } from '../hooks';
export const OrderDetailModal = ({ pedido, open, onClose, }) => {
    const [activeTab, setActiveTab] = useState('resumen');
    const { user } = useAuthStore();
    const transicionMutation = useTransicionEstado();
    const cancelarMutation = useCancelarPedido();
    // Estado para modal de cancelación
    const [cancelModal, setCancelModal] = useState({
        open: false,
        motivo: '',
        error: '',
    });
    // Handle loading state
    if (pedido === undefined) {
        return (_jsx(Modal, { isOpen: open, onClose: onClose, title: "Cargando...", children: _jsx("div", { className: "p-4 text-center", children: "Cargando detalles del pedido..." }) }));
    }
    // Handle no pedido selected
    if (pedido === null)
        return null;
    const userRoles = user?.roles || [];
    const transiciones = getTransicionesDisponibles(pedido.estado_codigo, userRoles);
    const formatPrice = (price) => {
        return new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS',
        }).format(price);
    };
    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('es-AR', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };
    const handleTransicion = (transicion) => {
        if (transicion.requires_motivo && transicion.nuevo_estado === 'CANCELADO') {
            setCancelModal({ open: true, motivo: '', error: '' });
            return;
        }
        transicionMutation.mutate({
            pedidoId: pedido.id,
            data: { nuevo_estado: transicion.nuevo_estado },
        }, {
            onSuccess: () => {
                onClose(); // Close modal after transition
            },
        });
    };
    const handleConfirmCancel = () => {
        if (!cancelModal.motivo.trim()) {
            setCancelModal((prev) => ({ ...prev, error: 'El motivo es obligatorio' }));
            return;
        }
        cancelarMutation.mutate({
            pedidoId: pedido.id,
            motivo: cancelModal.motivo,
        }, {
            onSuccess: () => {
                setCancelModal({ open: false, motivo: '', error: '' });
                onClose();
            },
        });
    };
    const tabs = [
        { id: 'resumen', label: 'Resumen' },
        { id: 'lineas', label: 'Líneas' },
        { id: 'historial', label: 'Historial' },
        { id: 'pago', label: 'Pago' },
    ];
    const renderTabContent = () => {
        switch (activeTab) {
            case 'resumen':
                return (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "ID" }), _jsxs("p", { className: "font-medium", children: ["#", pedido.id] })] }), _jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "Estado" }), _jsx("p", { children: _jsx("span", { className: `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ESTADO_COLORS[pedido.estado_codigo]}`, children: ESTADO_LABELS[pedido.estado_codigo] }) })] }), pedido.cliente && (_jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "Cliente" }), _jsxs("p", { className: "font-medium", children: [pedido.cliente.nombre || '', " (", pedido.cliente.email, ")"] })] })), _jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "Total" }), _jsx("p", { className: "font-medium", children: formatPrice(pedido.total) })] }), _jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "Costo env\u00EDo" }), _jsx("p", { className: "font-medium", children: formatPrice(pedido.costo_envio) })] }), _jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "Forma de pago" }), _jsx("p", { className: "font-medium", children: pedido.forma_pago_codigo })] }), _jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "Fecha" }), _jsx("p", { className: "font-medium", children: formatDate(pedido.created_at) })] }), pedido.direccion_id && (_jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "Direcci\u00F3n ID" }), _jsxs("p", { className: "font-medium", children: ["#", pedido.direccion_id] })] }))] }), pedido.notas && (_jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "Notas" }), _jsx("p", { className: "mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded", children: pedido.notas })] }))] }));
            case 'lineas':
                return (_jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full text-sm", children: [_jsx("thead", { className: "bg-gray-50 dark:bg-gray-700", children: _jsxs("tr", { children: [_jsx("th", { className: "px-3 py-2 text-left", children: "Producto" }), _jsx("th", { className: "px-3 py-2 text-right", children: "Cantidad" }), _jsx("th", { className: "px-3 py-2 text-right", children: "Precio" }), _jsx("th", { className: "px-3 py-2 text-right", children: "Subtotal" })] }) }), _jsx("tbody", { className: "divide-y divide-gray-200 dark:divide-gray-600", children: pedido.detalles.map((detalle) => (_jsxs("tr", { children: [_jsxs("td", { className: "px-3 py-2", children: [_jsx("div", { className: "font-medium", children: detalle.nombre_snapshot }), detalle.personalizacion && detalle.personalizacion.length > 0 && (_jsxs("div", { className: "text-xs text-gray-500", children: ["Sin: ", detalle.personalizacion.join(', ')] }))] }), _jsx("td", { className: "px-3 py-2 text-right", children: detalle.cantidad }), _jsx("td", { className: "px-3 py-2 text-right", children: formatPrice(detalle.precio_snapshot) }), _jsx("td", { className: "px-3 py-2 text-right", children: formatPrice(detalle.precio_snapshot * detalle.cantidad) })] }, detalle.id))) })] }) }));
            case 'historial':
                return _jsx(HistorialTimeline, { historial: pedido.historial });
            case 'pago':
                return (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("span", { className: "text-sm text-gray-500 dark:text-gray-400", children: "M\u00E9todo de pago" }), _jsx("p", { className: "font-medium", children: pedido.forma_pago_codigo })] }), _jsx("div", { className: "p-4 bg-gray-50 dark:bg-gray-700 rounded-lg text-center", children: _jsx("p", { className: "text-gray-500 dark:text-gray-400", children: "Informaci\u00F3n de pago del servidor no disponible en este change" }) })] }));
            default:
                return null;
        }
    };
    const modalActions = [
        { label: 'Cerrar', onClick: onClose, variant: 'secondary' },
        ...transiciones.map((t) => ({
            label: t.label,
            onClick: () => handleTransicion(t),
            variant: t.nuevo_estado === 'CANCELADO' ? 'danger' : 'primary',
        })),
    ];
    const isMutating = transicionMutation.isPending || cancelarMutation.isPending;
    // DEBUG: Show what's happening - MADE VERY VISIBLE
    const debugInfo = (_jsxs("div", { style: {
            backgroundColor: '#ff0000',
            color: 'white',
            padding: '20px',
            margin: '10px 0',
            fontSize: '16px',
            fontWeight: 'bold'
        }, children: [_jsx("div", { children: "\uD83D\uDEA8 DEBUG INFO:" }), _jsxs("div", { children: ["userRoles: ", JSON.stringify(userRoles)] }), _jsxs("div", { children: ["estado: ", pedido.estado_codigo] }), _jsxs("div", { children: ["transiciones: ", transiciones.length] }), transiciones.map((t, i) => (_jsxs("div", { style: { color: 'yellow' }, children: ["\uD83D\uDC49 ", t.label, " \u2192 ", t.nuevo_estado] }, i))), _jsxs("div", { children: ["actions array length: ", modalActions.length] })] }));
    return (_jsxs(_Fragment, { children: [_jsxs(Modal, { isOpen: open, onClose: onClose, title: `Pedido #${pedido.id}`, actions: modalActions, children: [_jsx("div", { className: isMutating ? 'opacity-50 pointer-events-none' : '', children: debugInfo }), _jsx("div", { className: "flex border-b border-gray-200 dark:border-gray-700 mb-4", children: tabs.map((tab) => (_jsx("button", { onClick: () => setActiveTab(tab.id), className: `px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${activeTab === tab.id
                                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`, children: tab.label }, tab.id))) }), _jsx("div", { className: "min-h-[300px]", children: renderTabContent() })] }), _jsx(Modal, { isOpen: cancelModal.open, onClose: () => setCancelModal({ open: false, motivo: '', error: '' }), title: "Cancelar Pedido", actions: [
                    { label: 'Cancelar', onClick: () => setCancelModal({ open: false, motivo: '', error: '' }), variant: 'secondary' },
                    { label: cancelarMutation.isPending ? 'Cancelando...' : 'Confirmar', onClick: handleConfirmCancel, variant: 'danger' },
                ], children: _jsxs("div", { className: "space-y-4", children: [_jsxs("p", { className: "text-gray-600 dark:text-gray-400", children: ["\u00BFEst\u00E1s seguro de que deseas cancelar el pedido #", pedido.id, "?"] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: ["Motivo de cancelaci\u00F3n ", _jsx("span", { className: "text-red-500", children: "*" })] }), _jsx("textarea", { value: cancelModal.motivo, onChange: (e) => setCancelModal((prev) => ({ ...prev, motivo: e.target.value, error: '' })), placeholder: "Ingrese el motivo de la cancelaci\u00F3n...", rows: 3, className: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100" }), cancelModal.error && (_jsx("p", { className: "text-red-500 text-sm mt-1", children: cancelModal.error }))] })] }) })] }));
};
export default OrderDetailModal;
//# sourceMappingURL=OrderDetailModal.js.map