import { jsx as _jsx } from "react/jsx-runtime";
/**
 * IngredientList.test.tsx
 * Unit tests for the IngredientList component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { IngredientList } from '../ui/IngredientList';
import * as api from '@/entities/ingrediente/api';
// Mock the API module
vi.mock('@/entities/ingrediente/api');
// Mock auth store
vi.mock('@/features/auth/store', () => ({
    useAuthStore: () => ({
        user: {
            id: 1,
            name: 'Test User',
            email: 'test@example.com',
            roles: ['STOCK', 'ADMIN'],
        },
    }),
    userHasRole: () => true,
}));
// Create a custom render function with query client
const createQueryClient = () => new QueryClient({
    defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
    },
});
const renderWithQueryClient = (component) => {
    const queryClient = createQueryClient();
    return render(_jsx(QueryClientProvider, { client: queryClient, children: component }));
};
describe('IngredientList Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });
    it('11.1a: renders list of ingredients from mock data', async () => {
        const mockIngredients = {
            items: [
                { id: 1, nombre: 'Tomate', es_alergeno: false, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00', deleted_at: null },
                { id: 2, nombre: 'Maní', es_alergeno: true, created_at: '2024-01-02T00:00:00', updated_at: '2024-01-02T00:00:00', deleted_at: null },
            ],
            total: 2,
            skip: 0,
            limit: 100,
        };
        vi.mocked(api.fetchIngredientes).mockResolvedValueOnce(mockIngredients);
        renderWithQueryClient(_jsx(IngredientList, {}));
        await waitFor(() => {
            expect(screen.getByText('Tomate')).toBeInTheDocument();
            expect(screen.getByText('Maní')).toBeInTheDocument();
        });
    });
    it('11.1b: Loading state displays spinner', async () => {
        vi.mocked(api.fetchIngredientes).mockImplementationOnce(() => new Promise(() => { })); // Never resolves
        renderWithQueryClient(_jsx(IngredientList, {}));
        await waitFor(() => {
            expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
        });
    });
    it('11.1c: Error state displays error message', async () => {
        vi.mocked(api.fetchIngredientes).mockRejectedValueOnce(new Error('API Error'));
        renderWithQueryClient(_jsx(IngredientList, {}));
        await waitFor(() => {
            expect(screen.getByText(/error/i)).toBeInTheDocument();
        });
    });
    it('11.1d: Edit button opens EditIngredientModal', async () => {
        const mockIngredients = {
            items: [
                { id: 1, nombre: 'Tomate', es_alergeno: false, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00', deleted_at: null },
            ],
            total: 1,
            skip: 0,
            limit: 100,
        };
        vi.mocked(api.fetchIngredientes).mockResolvedValueOnce(mockIngredients);
        renderWithQueryClient(_jsx(IngredientList, {}));
        await waitFor(() => {
            expect(screen.getByText('Tomate')).toBeInTheDocument();
        });
        const editButton = screen.getByTestId('edit-btn-1');
        fireEvent.click(editButton);
        await waitFor(() => {
            expect(screen.getByTestId('edit-ingredient-modal')).toBeInTheDocument();
        });
    });
    it('11.1e: Delete button opens DeleteConfirmModal', async () => {
        const mockIngredients = {
            items: [
                { id: 1, nombre: 'Tomate', es_alergeno: false, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00', deleted_at: null },
            ],
            total: 1,
            skip: 0,
            limit: 100,
        };
        vi.mocked(api.fetchIngredientes).mockResolvedValueOnce(mockIngredients);
        renderWithQueryClient(_jsx(IngredientList, {}));
        await waitFor(() => {
            expect(screen.getByText('Tomate')).toBeInTheDocument();
        });
        const deleteButton = screen.getByTestId('delete-btn-1');
        fireEvent.click(deleteButton);
        await waitFor(() => {
            expect(screen.getByTestId('delete-confirm-modal')).toBeInTheDocument();
        });
    });
});
//# sourceMappingURL=IngredientList.test.js.map