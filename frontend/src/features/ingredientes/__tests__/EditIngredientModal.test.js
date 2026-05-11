import { jsx as _jsx } from "react/jsx-runtime";
/**
 * EditIngredientModal.test.tsx
 * Unit tests for the EditIngredientModal component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { EditIngredientModal } from '../EditIngredientModal';
import * as api from '@/entities/ingrediente/api';
// Mock the API module
vi.mock('@/entities/ingrediente/api');
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
const mockIngredient = {
    id: 1,
    nombre: 'Tomate',
    es_alergeno: false,
    creado_en: '2024-01-01',
    actualizado_en: '2024-01-01',
    eliminado_en: null,
};
describe('EditIngredientModal Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });
    it('11.3a: Form pre-populates with ingredient data', async () => {
        const onClose = vi.fn();
        renderWithQueryClient(_jsx(EditIngredientModal, { isOpen: true, ingrediente: mockIngredient, onClose: onClose }));
        const nombreInput = screen.getByDisplayValue('Tomate');
        expect(nombreInput).toBeInTheDocument();
    });
    it('11.3b: Submit button updates ingredient', async () => {
        const user = userEvent.setup();
        const onClose = vi.fn();
        vi.mocked(api.updateIngrediente).mockResolvedValueOnce({
            ...mockIngredient,
            nombre: 'Tomate Rojo',
        });
        renderWithQueryClient(_jsx(EditIngredientModal, { isOpen: true, ingrediente: mockIngredient, onClose: onClose }));
        // Change nombre
        const nombreInput = screen.getByDisplayValue('Tomate');
        await user.clear(nombreInput);
        await user.type(nombreInput, 'Tomate Rojo');
        // Submit
        const submitButton = screen.getByText(/update/i);
        await user.click(submitButton);
        // Verify API was called with correct data
        await waitFor(() => {
            expect(api.updateIngrediente).toHaveBeenCalledWith(1, { nombre: 'Tomate Rojo' });
        });
    });
    it('11.3c: Success closes modal and refetches', async () => {
        const user = userEvent.setup();
        const onClose = vi.fn();
        vi.mocked(api.updateIngrediente).mockResolvedValueOnce({
            ...mockIngredient,
            nombre: 'Tomate Actualizado',
        });
        renderWithQueryClient(_jsx(EditIngredientModal, { isOpen: true, ingrediente: mockIngredient, onClose: onClose }));
        // Change and submit
        const nombreInput = screen.getByDisplayValue('Tomate');
        await user.clear(nombreInput);
        await user.type(nombreInput, 'Tomate Actualizado');
        const submitButton = screen.getByText(/update/i);
        await user.click(submitButton);
        // Should close modal and show success
        await waitFor(() => {
            expect(onClose).toHaveBeenCalled();
            expect(screen.getByText(/successfully updated/i)).toBeInTheDocument();
        });
    });
});
//# sourceMappingURL=EditIngredientModal.test.js.map