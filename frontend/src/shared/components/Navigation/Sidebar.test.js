import { jsx as _jsx } from "react/jsx-runtime";
/**
 * Sidebar component tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useAuthStore } from '@/features/auth/store';
// Mock useAuthStore
vi.mock('@/features/auth/store', () => ({
    useAuthStore: vi.fn(),
    userHasRole: (user, requiredRoles) => {
        if (!user)
            return false;
        return requiredRoles.some((role) => user.roles.includes(role));
    },
}));
// Mock useUIStore
vi.mock('@/features/ui/store', () => ({
    useUIStore: vi.fn(() => ({
        sidebarOpen: true,
    })),
}));
describe('Sidebar', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });
    it('renders menu items for ADMIN role', () => {
        vi.mocked(useAuthStore).mockReturnValue({
            user: { id: '1', email: 'admin@example.com', name: 'Admin User', roles: ['ADMIN'] },
            token: 'token',
            refreshToken: 'refreshToken',
            isAuthenticated: true,
            setUser: vi.fn(),
            setTokens: vi.fn(),
            logout: vi.fn(),
        });
        render(_jsx(BrowserRouter, { children: _jsx(Sidebar, { isOpen: true }) }));
        // ADMIN can see all items
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Usuarios')).toBeInTheDocument();
    });
    it('renders menu items for CLIENT role', () => {
        vi.mocked(useAuthStore).mockReturnValue({
            user: { id: '2', email: 'client@example.com', name: 'Client User', roles: ['CLIENT'] },
            token: 'token',
            refreshToken: 'refreshToken',
            isAuthenticated: true,
            setUser: vi.fn(),
            setTokens: vi.fn(),
            logout: vi.fn(),
        });
        render(_jsx(BrowserRouter, { children: _jsx(Sidebar, { isOpen: true }) }));
        // CLIENT should see specific items
        expect(screen.getByText('Catálogo')).toBeInTheDocument();
        expect(screen.getByText('Carrito')).toBeInTheDocument();
        expect(screen.getByText('Mis Pedidos')).toBeInTheDocument();
        // CLIENT should NOT see admin-only items
        expect(screen.queryByText('Usuarios')).not.toBeInTheDocument();
    });
    it('displays user info on desktop', () => {
        vi.mocked(useAuthStore).mockReturnValue({
            user: { id: '1', email: 'test@example.com', name: 'Test User', roles: ['ADMIN'] },
            token: 'token',
            refreshToken: 'refreshToken',
            isAuthenticated: true,
            setUser: vi.fn(),
            setTokens: vi.fn(),
            logout: vi.fn(),
        });
        render(_jsx(BrowserRouter, { children: _jsx(Sidebar, { isOpen: true }) }));
        expect(screen.getByText('Test User')).toBeInTheDocument();
        expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });
    it('renders menu items with correct links', () => {
        vi.mocked(useAuthStore).mockReturnValue({
            user: { id: '1', email: 'admin@example.com', name: 'Admin User', roles: ['ADMIN'] },
            token: 'token',
            refreshToken: 'refreshToken',
            isAuthenticated: true,
            setUser: vi.fn(),
            setTokens: vi.fn(),
            logout: vi.fn(),
        });
        render(_jsx(BrowserRouter, { children: _jsx(Sidebar, { isOpen: true }) }));
        // Check that links have correct href
        const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
        expect(dashboardLink).toHaveAttribute('href', '/app/dashboard');
    });
});
//# sourceMappingURL=Sidebar.test.js.map