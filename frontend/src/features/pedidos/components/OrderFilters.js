import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * OrderFilters - Filtros para el listado de pedidos
 */
import { useState, useEffect } from 'react';
import { Button } from '@/shared/ui';
import { ESTADO_LABELS } from '../types';
const ESTADOS_OPCIONES = [
    { value: '', label: 'Todos los estados' },
    ...Object.entries(ESTADO_LABELS).map(([value, label]) => ({
        value,
        label,
    })),
];
export const OrderFilters = ({ filtros, onChange }) => {
    const [estado, setEstado] = useState(filtros.estado || '');
    const [desde, setDesde] = useState(filtros.desde || '');
    const [hasta, setHasta] = useState(filtros.hasta || '');
    const [busqueda, setBusqueda] = useState(filtros.busqueda || '');
    // Sync with parent filtros prop
    useEffect(() => {
        setEstado(filtros.estado || '');
        setDesde(filtros.desde || '');
        setHasta(filtros.hasta || '');
        setBusqueda(filtros.busqueda || '');
    }, [filtros.estado, filtros.desde, filtros.hasta, filtros.busqueda]);
    const handleChange = (newFiltros) => {
        const updated = {
            ...filtros,
            ...newFiltros,
        };
        // Clear empty values
        if (!updated.estado)
            delete updated.estado;
        if (!updated.desde)
            delete updated.desde;
        if (!updated.hasta)
            delete updated.hasta;
        if (!updated.busqueda)
            delete updated.busqueda;
        onChange(updated);
    };
    const handleLimpiar = () => {
        setEstado('');
        setDesde('');
        setHasta('');
        setBusqueda('');
        onChange({});
    };
    const tieneFiltros = estado || desde || hasta || busqueda;
    return (_jsx("div", { className: "bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700", children: _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Estado" }), _jsx("select", { value: estado, onChange: (e) => handleChange({ estado: e.target.value || undefined }), className: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500", children: ESTADOS_OPCIONES.map((opt) => (_jsx("option", { value: opt.value, children: opt.label }, opt.value))) })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Desde" }), _jsx("input", { type: "date", value: desde, onChange: (e) => handleChange({ desde: e.target.value || undefined }), className: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Hasta" }), _jsx("input", { type: "date", value: hasta, onChange: (e) => handleChange({ hasta: e.target.value || undefined }), className: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Buscar" }), _jsx("input", { type: "text", value: busqueda, onChange: (e) => handleChange({ busqueda: e.target.value || undefined }), placeholder: "ID o cliente...", className: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" })] }), _jsx("div", { className: "flex items-end", children: _jsx(Button, { variant: "outline", onClick: handleLimpiar, disabled: !tieneFiltros, className: "w-full", children: "Limpiar" }) })] }) }));
};
export default OrderFilters;
//# sourceMappingURL=OrderFilters.js.map