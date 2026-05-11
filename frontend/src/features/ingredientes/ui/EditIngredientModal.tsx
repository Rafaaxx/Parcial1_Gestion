/**
 * EditIngredientModal component
 * Modal form for editing an existing ingredient
 */

import { useState, useEffect } from 'react';
import { useIngredienteDetail, useUpdateIngrediente } from '@/entities/ingrediente/hooks';
import type { IngredienteUpdate } from '@/entities/ingrediente/types';
import { Button, Modal, Spinner } from '@/shared/ui';

interface EditIngredientModalProps {
  ingredientId: number | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function EditIngredientModal({
  ingredientId,
  isOpen,
  onClose,
  onSuccess,
}: EditIngredientModalProps) {
  const [nombre, setNombre] = useState('');
  const [esAlergeno, setEsAlergeno] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: ingrediente, isLoading } = useIngredienteDetail(ingredientId || 0);
  const updateMutation = useUpdateIngrediente(ingredientId || 0);

  useEffect(() => {
    if (ingrediente) {
      setNombre(ingrediente.nombre);
      setEsAlergeno(ingrediente.es_alergeno);
    }
  }, [ingrediente]);

  const handleSubmit = async (e: React.FormEvent) => {
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
      } as IngredienteUpdate);

      onClose();
      onSuccess?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar ingrediente');
    }
  };

  if (isLoading) return <Spinner />;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Editar Ingrediente">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="text-red-500 text-sm">{error}</div>}

        <div>
          <label htmlFor="nombre" className="block text-sm font-medium">
            Nombre
          </label>
          <input
            id="nombre"
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            id="esAlergeno"
            type="checkbox"
            checked={esAlergeno}
            onChange={(e) => setEsAlergeno(e.target.checked)}
            className="rounded border-gray-300"
          />
          <label htmlFor="esAlergeno" className="text-sm font-medium">
            Es un alérgeno
          </label>
        </div>

        <div className="flex gap-2 justify-end pt-4">
          <Button variant="secondary" onClick={onClose} type="button">
            Cancelar
          </Button>
          <Button
            type="submit"
            disabled={updateMutation.isPending}
            className="bg-blue-600 text-white hover:bg-blue-700"
          >
            {updateMutation.isPending ? 'Guardando...' : 'Guardar'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
