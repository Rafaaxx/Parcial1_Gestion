import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * AdminOrders — Order management with FSM (State Machine)
 * CHANGE-11: Panel de Gestión de Pedidos (Admin)
 */
import React, { useState } from 'react';
import { usePedidos, usePedidoDetail, useTransicionEstado, useCancelarPedido } from '@/features/pedidos';
import { OrderFilters, OrderDetailModal } from '@/features/pedidos/components';
import { Button, Toast } from '@/shared/ui';
import { ESTADO_LABELS, ESTADO_COLORS, } from '@/features/pedidos/types';
// Componente para mostrar el badge de estado
const EstadoBadge = ({ estado }) => {
    const colorClass = ESTADO_COLORS[estado] || 'bg-gray-100 text-gray-800';
    const label = ESTADO_LABELS[estado] || estado;
    return (_jsx("span", { className: `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`, children: label }));
};
// Componente para mostrar info del cliente
const ClienteCell = ({ pedido }) => {
    if (!pedido.cliente) {
        return _jsx("span", { className: "text-gray-400", children: "-" });
    }
    const { nombre, email } = pedido.cliente;
    const displayName = nombre || email;
    return (_jsxs("div", { className: "text-sm", children: [nombre && _jsx("div", { className: "font-medium text-gray-900 dark:text-gray-100", children: nombre }), _jsx("div", { className: "text-gray-500 dark:text-gray-400", children: email })] }));
};
// Componente principal
export const AdminOrders = () => {
    const [skip, setSkip] = useState(0);
    const limit = 20;
    // State for filters
    const [filtros, setFiltros] = useState({});
    // State for modal
    const [selectedPedidoId, setSelectedPedidoId] = useState(null);
    const [detailModalOpen, setDetailModalOpen] = useState(false);
    // Queries
    const { data, isLoading, error, refetch } = usePedidos(skip, limit, filtros);
    const { data: pedidoDetalle, isLoading: detailLoading } = usePedidoDetail(selectedPedidoId || 0);
    const transicionMutation = useTransicionEstado();
    const cancelarMutation = useCancelarPedido();
    // Estado para toast
    const [toast, setToast] = useState({
        open: false,
        type: 'success',
        message: '',
    });
    // Mostrar toast de error de mutación
    React.useEffect(() => {
        if (transicionMutation.isError) {
            setToast({
                open: true,
                type: 'error',
                message: transicionMutation.error?.message || 'Error al cambiar estado',
            });
        }
    }, [transicionMutation.isError, transicionMutation.error]);
    // Reset pagination when filters change
    const handleFiltrosChange = (newFiltros) => {
        setFiltros(newFiltros);
        setSkip(0); // Reset to first page
    };
    // Open detail modal
    const handleRowClick = (pedido) => {
        setSelectedPedidoId(pedido.id);
        setDetailModalOpen(true);
    };
    // Close detail modal
    const handleCloseDetail = () => {
        setDetailModalOpen(false);
        setSelectedPedidoId(null);
        refetch(); // Refresh list after potential changes
    };
    // Calcular paginación
    const total = data?.total || 0;
    const hasNext = skip + limit < total;
    const hasPrev = skip > 0;
    // Formatear precio
    const formatPrice = (price) => {
        return new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS',
        }).format(price);
    };
    // Formatear fecha
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
    return (_jsxs("div", { className: "space-y-6", children: [_jsx("h1", { className: "text-2xl font-bold text-gray-900 dark:text-gray-50", children: "Gesti\u00F3n de Pedidos" }), _jsx(OrderFilters, { filtros: filtros, onChange: handleFiltrosChange }), _jsxs("div", { className: "card-base overflow-hidden", children: [isLoading ? (_jsx("div", { className: "p-8 text-center text-gray-500", children: "Cargando pedidos..." })) : error ? (_jsxs("div", { className: "p-8 text-center text-red-500", children: ["Error al cargar pedidos: ", error.message] })) : !data?.items.length ? (_jsxs("div", { className: "p-12 text-center", children: [_jsx("span", { className: "text-5xl block mb-4", children: "\uD83D\uDCCB" }), _jsx("h2", { className: "text-xl font-semibold text-gray-900 dark:text-gray-50 mb-2", children: "No hay pedidos" }), _jsx("p", { className: "text-gray-600 dark:text-gray-400", children: Object.keys(filtros).length > 0
                                    ? 'No hay pedidos que coincidan con los filtros aplicados'
                                    : 'Los pedidos aparecerán aquí cuando se creen.' })] })) : (_jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { className: "bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700", children: _jsxs("tr", { children: [_jsx("th", { className: "px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider", children: "ID" }), _jsx("th", { className: "px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider", children: "Cliente" }), _jsx("th", { className: "px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider", children: "Estado" }), _jsx("th", { className: "px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider", children: "Total" }), _jsx("th", { className: "px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider", children: "Fecha" })] }) }), _jsx("tbody", { className: "divide-y divide-gray-200 dark:divide-gray-700", children: data.items.map((pedido) => (_jsxs("tr", { className: "hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer", onClick: () => handleRowClick(pedido), children: [_jsxs("td", { className: "px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-50", children: ["#", pedido.id] }), _jsx("td", { className: "px-4 py-4 whitespace-nowrap", children: _jsx(ClienteCell, { pedido: pedido }) }), _jsx("td", { className: "px-4 py-4 whitespace-nowrap", children: _jsx(EstadoBadge, { estado: pedido.estado_codigo }) }), _jsx("td", { className: "px-4 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400", children: formatPrice(pedido.total) }), _jsx("td", { className: "px-4 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400", children: formatDate(pedido.created_at) })] }, pedido.id))) })] }) })), total > 0 && (_jsxs("div", { className: "px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700", children: [_jsx("div", { className: "text-sm text-gray-500 dark:text-gray-400", children: total === 0
                                    ? 'Sin resultados'
                                    : `Mostrando ${skip + 1} - ${Math.min(skip + limit, total)} de ${total}` }), _jsxs("div", { className: "flex gap-2", children: [_jsx(Button, { variant: "outline", size: "sm", disabled: !hasPrev, onClick: () => setSkip(Math.max(0, skip - limit)), children: "Anterior" }), _jsx(Button, { variant: "outline", size: "sm", disabled: !hasNext, onClick: () => setSkip(skip + limit), children: "Siguiente" })] })] }))] }), _jsx(OrderDetailModal, { pedido: detailModalOpen && selectedPedidoId ? pedidoDetalle || null : null, open: detailModalOpen, onClose: handleCloseDetail }), _jsx(Toast, { open: toast.open, onClose: () => setToast((prev) => ({ ...prev, open: false })), type: toast.type, message: toast.message })] }));
};
export default AdminOrders;
//# sourceMappingURL=AdminOrders.js.map