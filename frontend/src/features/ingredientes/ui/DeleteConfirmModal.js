import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * DeleteConfirmModal component
 * Modal for confirming ingredient deletion
 */
import { useState } from 'react';
import { useDeleteIngrediente } from '@/entities/ingrediente/hooks';
import { Button } from '@/shared/ui/button';
import { Modal } from '@/shared/ui/modal';
export function DeleteConfirmModal({ ingredientId, ingredientName, isOpen, onClose, onSuccess, }) {
    const [error, setError] = useState(null);
    const deleteMutation = useDeleteIngrediente(ingredientId || 0);
    const handleDelete = async () => {
        setError(null);
        try {
            await deleteMutation.mutateAsync();
            onClose();
            onSuccess?.();
        }
        catch (err) {
            setError(err.response?.data?.detail || 'Error al eliminar ingrediente');
        }
    };
    return (_jsx(Modal, { isOpen: isOpen, onClose: onClose, title: "Confirmar eliminaci\u00F3n", variant: "destructive", children: _jsxs("div", { className: "space-y-4", children: [error && _jsx("div", { className: "text-red-500 text-sm", children: error }), _jsxs("p", { className: "text-gray-700", children: ["\u00BFEst\u00E1 seguro de que desea eliminar el ingrediente ", _jsx("strong", { children: ingredientName }), "?"] }), _jsx("p", { className: "text-sm text-gray-600", children: "Esta acci\u00F3n es irreversible. El ingrediente ser\u00E1 marcado como eliminado." }), _jsxs("div", { className: "flex gap-2 justify-end pt-4", children: [_jsx(Button, { variant: "secondary", onClick: onClose, type: "button", children: "Cancelar" }), _jsx(Button, { variant: "destructive", onClick: handleDelete, disabled: deleteMutation.isPending, children: deleteMutation.isPending ? 'Eliminando...' : 'Eliminar' })] })] }) }));
}
//# sourceMappingURL=DeleteConfirmModal.js.map