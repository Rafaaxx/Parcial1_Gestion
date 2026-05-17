/**
 * Ingredientes admin page
 * Lists all ingredients with CRUD operations (only for STOCK/ADMIN roles)
 */

import React, { useState } from 'react';
import { IngredientList } from '@/features/ingredientes/ui';
import { CreateIngredientModal } from '@/features/ingredientes/ui/CreateIngredientModal';
import { EditIngredientModal } from '@/features/ingredientes/ui/EditIngredientModal';
import { DeleteConfirmModal } from '@/features/ingredientes/ui/DeleteConfirmModal';
import { Button } from '@/shared/ui/Button';

const IngredientsAdminPage: React.FC = () => {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const handleEdit = (id: number) => {
    setEditingId(id)
  }

  const handleDelete = (id: number) => {
    setDeletingId(id)
  }

  return (
    <div className="p-8">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Ingredientes</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Gestiona los ingredientes y sus alérgenos
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          + Nuevo Ingrediente
        </Button>
      </div>

      <IngredientList onEdit={handleEdit} onDelete={handleDelete} />

      <CreateIngredientModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={() => setShowCreateModal(false)}
      />

      <EditIngredientModal
        ingredientId={editingId}
        isOpen={!!editingId}
        onClose={() => setEditingId(null)}
        onSuccess={() => setEditingId(null)}
      />

      <DeleteConfirmModal
        ingredientId={deletingId}
        isOpen={!!deletingId}
        onClose={() => setDeletingId(null)}
        onSuccess={() => setDeletingId(null)}
        ingredientName=""
      />
    </div>
  );
};

export default IngredientsAdminPage;
