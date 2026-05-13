import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * IngredientList component
 * Displays a table of active ingredients with pagination and filters
 */
import { useState } from 'react';
import { useIngredientes } from '@/entities/ingrediente/hooks';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { Spinner } from '@/shared/ui/Spinner';
export function IngredientList({ onEdit, onDelete, readonly = false }) {
    const [skip, setSkip] = useState(0);
    const [limit, setLimit] = useState(20);
    const [esAlergeno, setEsAlergeno] = useState(undefined);
    const { data, isLoading, error } = useIngredientes(skip, limit, esAlergeno);
    if (isLoading)
        return _jsx(Spinner, {});
    if (error)
        return _jsx("div", { className: "text-red-500", children: "Error loading ingredients" });
    if (!data)
        return _jsx("div", { children: "No data" });
    return (_jsxs("div", { className: "space-y-4", children: [_jsx("div", { className: "flex gap-2 items-center", children: _jsxs("label", { className: "flex items-center gap-2", children: [_jsx("input", { type: "checkbox", checked: esAlergeno === true, onChange: (e) => setEsAlergeno(e.target.checked ? true : undefined), className: "rounded border-gray-300" }), "Mostrar solo al\u00E9rgenos"] }) }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full border-collapse border border-gray-300", children: [_jsx("thead", { className: "bg-gray-100", children: _jsxs("tr", { children: [_jsx("th", { className: "border border-gray-300 px-4 py-2 text-left", children: "Nombre" }), _jsx("th", { className: "border border-gray-300 px-4 py-2 text-center", children: "Al\u00E9rgeno" }), _jsx("th", { className: "border border-gray-300 px-4 py-2 text-left", children: "Creado" }), !readonly && _jsx("th", { className: "border border-gray-300 px-4 py-2", children: "Acciones" })] }) }), _jsx("tbody", { children: data.items.map((ingrediente) => (_jsxs("tr", { className: "hover:bg-gray-50", children: [_jsx("td", { className: "border border-gray-300 px-4 py-2", children: ingrediente.nombre }), _jsx("td", { className: "border border-gray-300 px-4 py-2 text-center", children: ingrediente.es_alergeno && _jsx(Badge, { variant: "warning", children: "Al\u00E9rgeno" }) }), _jsx("td", { className: "border border-gray-300 px-4 py-2 text-sm text-gray-600", children: new Date(ingrediente.created_at).toLocaleDateString() }), !readonly && (_jsxs("td", { className: "border border-gray-300 px-4 py-2 space-x-2", children: [onEdit && (_jsx(Button, { variant: "secondary", onClick: () => onEdit(ingrediente.id), children: "Editar" })), onDelete && (_jsx(Button, { variant: "danger", onClick: () => onDelete(ingrediente.id), children: "Eliminar" }))] }))] }, ingrediente.id))) })] }) }), _jsxs("div", { className: "flex justify-between items-center", children: [_jsxs("div", { className: "text-sm text-gray-600", children: ["Mostrando ", data.items.length, " de ", data.total, " ingredientes"] }), _jsxs("div", { className: "space-x-2", children: [_jsx(Button, { disabled: skip === 0, onClick: () => setSkip(Math.max(0, skip - limit)), children: "Anterior" }), _jsx(Button, { disabled: skip + limit >= data.total, onClick: () => setSkip(skip + limit), children: "Siguiente" })] })] })] }));
}
//# sourceMappingURL=IngredientList.js.map