import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * EditIngredientModal component
 * Modal form for editing an existing ingredient
 */
import { useState, useEffect } from 'react';
import { useIngredienteDetail, useUpdateIngrediente } from '@/entities/ingrediente/hooks';
import { Button } from '@/shared/ui/Button';
import { Modal } from '@/shared/ui/Modal';
import { Spinner } from '@/shared/ui/Spinner';
export function EditIngredientModal({ ingredientId, isOpen, onClose, onSuccess, }) {
    const [nombre, setNombre] = useState('');
    const [esAlergeno, setEsAlergeno] = useState(false);
    const [error, setError] = useState(null);
    const { data: ingrediente, isLoading } = useIngredienteDetail(ingredientId || 0);
    const updateMutation = useUpdateIngrediente(ingredientId || 0);
    useEffect(() => {
        if (ingrediente) {
            setNombre(ingrediente.nombre);
            setEsAlergeno(ingrediente.es_alergeno);
        }
    }, [ingrediente]);
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        if (!nombre.trim()) {
            setError('El nombre es requerido');
            return;
        }
        try {
            await updateMutation.mutateAsync({
                nombre: nombre.trim(),
                es_alergeno: esAlergeno,
            });
            onClose();
            onSuccess?.();
        }
        catch (err) {
            setError(err.response?.data?.detail || 'Error al actualizar ingrediente');
        }
    };
    if (isLoading)
        return _jsx(Spinner, {});
    return (_jsx(Modal, { isOpen: isOpen, onClose: onClose, title: "Editar Ingrediente", children: _jsxs("form", { onSubmit: handleSubmit, className: "space-y-4", children: [error && _jsx("div", { className: "text-red-500 text-sm", children: error }), _jsxs("div", { children: [_jsx("label", { htmlFor: "nombre", className: "block text-sm font-medium", children: "Nombre" }), _jsx("input", { id: "nombre", type: "text", value: nombre, onChange: (e) => setNombre(e.target.value), className: "w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", required: true })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("input", { id: "esAlergeno", type: "checkbox", checked: esAlergeno, onChange: (e) => setEsAlergeno(e.target.checked), className: "rounded border-gray-300" }), _jsx("label", { htmlFor: "esAlergeno", className: "text-sm font-medium", children: "Es un al\u00E9rgeno" })] }), _jsxs("div", { className: "flex gap-2 justify-end pt-4", children: [_jsx(Button, { variant: "secondary", onClick: onClose, type: "button", children: "Cancelar" }), _jsx(Button, { type: "submit", disabled: updateMutation.isPending, className: "bg-blue-600 text-white hover:bg-blue-700", children: updateMutation.isPending ? 'Guardando...' : 'Guardar' })] })] }) }));
}
//# sourceMappingURL=EditIngredientModal.js.map