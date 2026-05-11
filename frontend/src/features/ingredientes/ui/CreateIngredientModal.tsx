/**
 * CreateIngredientModal component
 * Modal form for creating a new ingredient
 */

import { useState } from 'react';
import { useCreateIngrediente } from '@/entities/ingrediente/hooks';
import type { IngredienteCreate } from '@/entities/ingrediente/types';
import { Button } from '@/shared/ui/button';
import { Modal } from '@/shared/ui/modal';

interface CreateIngredientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function CreateIngredientModal({ isOpen, onClose, onSuccess }: CreateIngredientModalProps) {
  const [nombre, setNombre] = useState('');
  const [esAlergeno, setEsAlergeno] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createMutation = useCreateIngrediente();

  const handleSubmit = async (e: React.FormEvent) => {
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
      } as IngredienteCreate);

      setNombre('');
      setEsAlergeno(false);
      onClose();
      onSuccess?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear ingrediente');
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Crear Ingrediente">
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
            placeholder="Ej: Gluten"
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
            disabled={createMutation.isPending}
            className="bg-blue-600 text-white hover:bg-blue-700"
          >
            {createMutation.isPending ? 'Creando...' : 'Crear'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
