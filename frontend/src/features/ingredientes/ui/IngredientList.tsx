/**
 * IngredientList component
 * Displays a table of active ingredients with pagination and filters
 */

import { useState } from 'react';
import { useIngredientes } from '@/entities/ingrediente/hooks';
import { Badge, Button, Spinner } from '@/shared/ui';

interface IngredientListProps {
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  readonly?: boolean;
}

export function IngredientList({ onEdit, onDelete, readonly = false }: IngredientListProps) {
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(20);
  const [esAlergeno, setEsAlergeno] = useState<boolean | undefined>(undefined);

  const { data, isLoading, error } = useIngredientes(skip, limit, esAlergeno);

  if (isLoading) return <Spinner />;
  if (error) return <div className="text-red-500">Error loading ingredients</div>;
  if (!data) return <div>No data</div>;

  return (
    <div className="space-y-4">
      {/* Filter controls */}
      <div className="flex gap-2 items-center">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={esAlergeno === true}
            onChange={(e) => setEsAlergeno(e.target.checked ? true : undefined)}
            className="rounded border-gray-300"
          />
          Mostrar solo alérgenos
        </label>
      </div>

      {/* Ingredients table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 px-4 py-2 text-left">Nombre</th>
              <th className="border border-gray-300 px-4 py-2 text-center">Alérgeno</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Creado</th>
              {!readonly && <th className="border border-gray-300 px-4 py-2">Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {data.items.map((ingrediente) => (
              <tr key={ingrediente.id} className="hover:bg-gray-50">
                <td className="border border-gray-300 px-4 py-2">{ingrediente.nombre}</td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  {ingrediente.es_alergeno && <Badge variant="warning">Alérgeno</Badge>}
                </td>
                <td className="border border-gray-300 px-4 py-2 text-sm text-gray-600">
                  {new Date(ingrediente.created_at).toLocaleDateString()}
                </td>
                {!readonly && (
                  <td className="border border-gray-300 px-4 py-2 space-x-2">
                    {onEdit && (
                      <Button size="sm" variant="secondary" onClick={() => onEdit(ingrediente.id)}>
                        Editar
                      </Button>
                    )}
                    {onDelete && (
                       <Button
                         size="sm"
                         variant="danger"
                         onClick={() => onDelete(ingrediente.id)}
                       >
                         Eliminar
                       </Button>
                     )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination controls */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          Mostrando {data.items.length} de {data.total} ingredientes
        </div>
        <div className="space-x-2">
          <Button disabled={skip === 0} onClick={() => setSkip(Math.max(0, skip - limit))}>
            Anterior
          </Button>
          <Button disabled={skip + limit >= data.total} onClick={() => setSkip(skip + limit)}>
            Siguiente
          </Button>
        </div>
      </div>
    </div>
  );
}
