/**
 * ProtectedRoute HOC tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { useAuthStore } from '@/features/auth/store';

// Mock useAuthStore
vi.mock('@/features/auth/store', () => ({
  useAuthStore: vi.fn(),
  userHasRole: (user, requiredRoles) => {
    if (!user) return false;
    return requiredRoles.some((role) => user.roles.includes(role));
  },
}));

const TestComponent = () => <div>Protected Content</div>;

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders children when user is authenticated with correct role', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: '1', email: 'test@example.com', name: 'Test User', roles: ['ADMIN'] },
      token: 'token',
      refreshToken: 'refreshToken',
      isAuthenticated: true,
      setUser: vi.fn(),
      setTokens: vi.fn(),
      logout: vi.fn(),
    } as any);

    render(
      <BrowserRouter>
        <ProtectedRoute requiredRoles={['ADMIN']}>
          <TestComponent />
        </ProtectedRoute>
      </BrowserRouter>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('redirects to /login when user is not authenticated', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      setUser: vi.fn(),
      setTokens: vi.fn(),
      logout: vi.fn(),
    } as any);

    render(
      <BrowserRouter>
        <ProtectedRoute requiredRoles={['ADMIN']}>
          <TestComponent />
        </ProtectedRoute>
      </BrowserRouter>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('redirects to /unauthorized when user lacks required role', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: '1', email: 'test@example.com', name: 'Test User', roles: ['CLIENT'] },
      token: 'token',
      refreshToken: 'refreshToken',
      isAuthenticated: true,
      setUser: vi.fn(),
      setTokens: vi.fn(),
      logout: vi.fn(),
    } as any);

    render(
      <BrowserRouter>
        <ProtectedRoute requiredRoles={['ADMIN']}>
          <TestComponent />
        </ProtectedRoute>
      </BrowserRouter>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('renders children when no required roles are specified', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: '1', email: 'test@example.com', name: 'Test User', roles: ['CLIENT'] },
      token: 'token',
      refreshToken: 'refreshToken',
      isAuthenticated: true,
      setUser: vi.fn(),
      setTokens: vi.fn(),
      logout: vi.fn(),
    } as any);

    render(
      <BrowserRouter>
        <ProtectedRoute requiredRoles={[]}>
          <TestComponent />
        </ProtectedRoute>
      </BrowserRouter>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
});
