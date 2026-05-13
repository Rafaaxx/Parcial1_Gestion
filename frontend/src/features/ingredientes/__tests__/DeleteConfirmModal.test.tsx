/**
 * DeleteConfirmModal.test.tsx
 * Unit tests for the DeleteConfirmModal component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { DeleteConfirmModal } from '../ui/DeleteConfirmModal';
import * as api from '@/entities/ingrediente/api';

// Mock the API module
vi.mock('@/entities/ingrediente/api');

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('DeleteConfirmModal Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('11.4a: Delete button calls delete mutation', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const ingredienteId = 1;

    vi.mocked(api.deleteIngrediente).mockResolvedValueOnce(void 0);

    renderWithQueryClient(
      <DeleteConfirmModal
        isOpen={true}
        ingredienteId={ingredienteId}
        onClose={onClose}
      />
    );

    // Click delete button
    const deleteButton = screen.getByText(/delete/i);
    await user.click(deleteButton);

    // Verify API was called
    await waitFor(() => {
      expect(api.deleteIngrediente).toHaveBeenCalledWith(ingredienteId);
    });
  });

  it('11.4b: Success closes modal and refetches', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const ingredienteId = 1;

    vi.mocked(api.deleteIngrediente).mockResolvedValueOnce(void 0);

    renderWithQueryClient(
      <DeleteConfirmModal
        isOpen={true}
        ingredienteId={ingredienteId}
        onClose={onClose}
      />
    );

    // Click delete
    const deleteButton = screen.getByText(/delete/i);
    await user.click(deleteButton);

    // Should close modal and show success
    await waitFor(() => {
      expect(onClose).toHaveBeenCalled();
      expect(screen.getByText(/successfully deleted/i)).toBeInTheDocument();
    });
  });
});
