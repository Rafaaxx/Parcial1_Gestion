import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * CreateIngredientModal component
 * Modal form for creating a new ingredient
 */
import { useState } from 'react';
import { useCreateIngrediente } from '@/entities/ingrediente/hooks';
import { Button } from '@/shared/ui/Button';
import { Modal } from '@/shared/ui/Modal';
export function CreateIngredientModal({ isOpen, onClose, onSuccess }) {
    const [nombre, setNombre] = useState('');
    const [esAlergeno, setEsAlergeno] = useState(false);
    const [error, setError] = useState(null);
    const createMutation = useCreateIngrediente();
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        if (!nombre.trim()) {
            setError('El nombre es requerido');
            return;
        }
        try {
            await createMutation.mutateAsync({
                nombre: nombre.trim(),
                es_alergeno: esAlergeno,
            });
            setNombre('');
            setEsAlergeno(false);
            onClose();
            onSuccess?.();
        }
        catch (err) {
            setError(err.response?.data?.detail || 'Error al crear ingrediente');
        }
    };
    return (_jsx(Modal, { isOpen: isOpen, onClose: onClose, title: "Crear Ingrediente", children: _jsxs("form", { onSubmit: handleSubmit, className: "space-y-4", children: [error && _jsx("div", { className: "text-red-500 text-sm", children: error }), _jsxs("div", { children: [_jsx("label", { htmlFor: "nombre", className: "block text-sm font-medium", children: "Nombre" }), _jsx("input", { id: "nombre", type: "text", value: nombre, onChange: (e) => setNombre(e.target.value), placeholder: "Ej: Gluten", className: "w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", required: true })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("input", { id: "esAlergeno", type: "checkbox", checked: esAlergeno, onChange: (e) => setEsAlergeno(e.target.checked), className: "rounded border-gray-300" }), _jsx("label", { htmlFor: "esAlergeno", className: "text-sm font-medium", children: "Es un al\u00E9rgeno" })] }), _jsxs("div", { className: "flex gap-2 justify-end pt-4", children: [_jsx(Button, { variant: "secondary", onClick: onClose, type: "button", children: "Cancelar" }), _jsx(Button, { type: "submit", disabled: createMutation.isPending, className: "bg-blue-600 text-white hover:bg-blue-700", children: createMutation.isPending ? 'Creando...' : 'Crear' })] })] }) }));
}
//# sourceMappingURL=CreateIngredientModal.js.map