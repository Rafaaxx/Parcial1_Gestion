/**
 * CreateIngredientModal.test.tsx
 * Unit tests for the CreateIngredientModal component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { CreateIngredientModal } from '../CreateIngredientModal';
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
  return render(<QueryClientProvider client={queryClient}>{component}</QueryClientProvider>);
};

describe('CreateIngredientModal Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('11.2a: Form submission validates non-empty nombre', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    renderWithQueryClient(<CreateIngredientModal isOpen={true} onClose={onClose} />);

    // Try to submit empty form
    const submitButton = screen.getByText(/create/i);
    await user.click(submitButton);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/nombre is required/i)).toBeInTheDocument();
    });

    // API should not be called
    expect(api.createIngrediente).not.toHaveBeenCalled();
  });

  it('11.2b: Submit button disabled during mutation', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    // Mock API to never resolve
    vi.mocked(api.createIngrediente).mockImplementationOnce(() => new Promise(() => {}));

    renderWithQueryClient(<CreateIngredientModal isOpen={true} onClose={onClose} />);

    // Fill in the form
    const nombreInput = screen.getByPlaceholderText(/ingredient name/i);
    await user.type(nombreInput, 'Nuevo Ingrediente');

    // Submit
    const submitButton = screen.getByText(/create/i);
    await user.click(submitButton);

    // Button should be disabled
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });

  it('11.2c: Success closes modal and shows toast', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    vi.mocked(api.createIngrediente).mockResolvedValueOnce({
      id: 1,
      nombre: 'Tomate',
      es_alergeno: false,
      creado_en: '2024-01-01',
      actualizado_en: '2024-01-01',
      eliminado_en: null,
    });

    renderWithQueryClient(<CreateIngredientModal isOpen={true} onClose={onClose} />);

    // Fill form
    const nombreInput = screen.getByPlaceholderText(/ingredient name/i);
    await user.type(nombreInput, 'Tomate');

    // Submit
    const submitButton = screen.getByText(/create/i);
    await user.click(submitButton);

    // Should close modal and show success
    await waitFor(() => {
      expect(onClose).toHaveBeenCalled();
      expect(screen.getByText(/successfully created/i)).toBeInTheDocument();
    });
  });

  it('11.2d: Error displays error message', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    vi.mocked(api.createIngrediente).mockRejectedValueOnce(new Error('Duplicate nombre'));

    renderWithQueryClient(<CreateIngredientModal isOpen={true} onClose={onClose} />);

    // Fill form
    const nombreInput = screen.getByPlaceholderText(/ingredient name/i);
    await user.type(nombreInput, 'Duplicado');

    // Submit
    const submitButton = screen.getByText(/create/i);
    await user.click(submitButton);

    // Should show error
    await waitFor(() => {
      expect(screen.getByText(/duplicate nombre/i)).toBeInTheDocument();
    });

    // Modal should stay open
    expect(onClose).not.toHaveBeenCalled();
  });
});
