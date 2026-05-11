/**
 * DeleteConfirmModal component
 * Modal for confirming ingredient deletion
 */

import { useState } from 'react';
import { useDeleteIngrediente } from '@/entities/ingrediente/hooks';
import { Button } from '@/shared/ui/button';
import { Modal } from '@/shared/ui/modal';

interface DeleteConfirmModalProps {
  ingredientId: number | null;
  ingredientName?: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function DeleteConfirmModal({
  ingredientId,
  ingredientName,
  isOpen,
  onClose,
  onSuccess,
}: DeleteConfirmModalProps) {
  const [error, setError] = useState<string | null>(null);
  const deleteMutation = useDeleteIngrediente(ingredientId || 0);

  const handleDelete = async () => {
    setError(null);

    try {
      await deleteMutation.mutateAsync();
      onClose();
      onSuccess?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar ingrediente');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Confirmar eliminación"
      variant="destructive"
    >
      <div className="space-y-4">
        {error && <div className="text-red-500 text-sm">{error}</div>}

        <p className="text-gray-700">
          ¿Está seguro de que desea eliminar el ingrediente <strong>{ingredientName}</strong>?
        </p>
        <p className="text-sm text-gray-600">
          Esta acción es irreversible. El ingrediente será marcado como eliminado.
        </p>

        <div className="flex gap-2 justify-end pt-4">
          <Button variant="secondary" onClick={onClose} type="button">
            Cancelar
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
