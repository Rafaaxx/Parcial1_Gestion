## Context

Food Store currently has no navigation layer. The frontend needs a unified way to:
1. Display different menu options based on user role (CLIENT, STOCK, PEDIDOS, ADMIN)
2. Guard routes at the UI level (redirect unauthenticated users to /login, show 403 for unauthorized roles)
3. Wrap all protected pages with a consistent layout (header + sidebar + content)
4. Support responsive design (sidebar collapses on mobile)

Current authStore persists the access token and user object (with roles array). Frontend has no route guards or menu system yet. All routes are flat and unauthenticated access is possible to any page.

## Goals / Non-Goals

**Goals:**
- Implement ProtectedRoute HOC that validates authentication and role authorization before rendering
- Create Header and Sidebar components that render role-specific menu items
- Create Layout wrapper component that renders header + sidebar + outlet for all protected routes
- Create Unauthorized (403) error page for role mismatch cases
- Redirect unauthenticated users to /login automatically
- Lazy load module-specific pages (Products, Orders, Admin Dashboard) to reduce initial bundle size
- Support mobile-responsive sidebar (collapse/expand toggle)

**Non-Goals:**
- Backend API changes (no new endpoints)
- Database schema changes
- Changing how authStore works or JWT validation
- Implementing actual page contents (only the shell/layout)
- Implementing permission-level granularity (role-only for MVP)

## Decisions

### Decision 1: ProtectedRoute as HOC vs Wrapper Component
**Choice**: HOC (Higher-Order Component) pattern
**Rationale**: 
- Simpler to apply to individual routes in the router config
- Cleaner syntax: `<Route path="/products" element={<ProtectedRoute roles={['ADMIN', 'STOCK']}><ProductsPage /></ProtectedRoute>} />`
- Alternative (wrapper component on every page) would be more repetitive

**Implementation**: 
```typescript
export const ProtectedRoute: React.FC<{
  roles?: string[];
  children: React.ReactNode;
}> = ({ roles, children }) => {
  const { isAuthenticated, user } = useAuthStore(s => ({
    isAuthenticated: s.isAuthenticated,
    user: s.user
  }));
  const navigate = useNavigate();

  if (!isAuthenticated) {
    navigate('/login', { replace: true });
    return null;
  }

  if (roles && !user?.roles.some(r => roles.includes(r))) {
    return <Unauthorized />;
  }

  return <>{children}</>;
};
```

### Decision 2: Sidebar State Management
**Choice**: Zustand `uiStore` (non-persisted)
**Rationale**:
- UI state (sidebar open/closed) is transitional, not critical to persist
- Zustand already exists for UI state (cartOpen, etc.)
- Simpler than adding context or props drilling
- Reset on page refresh is acceptable UX

### Decision 3: Menu Structure
**Choice**: Role-based conditional rendering in Sidebar, not dynamic fetch
**Rationale**:
- Menu items are static and defined by role constants
- Avoids extra API calls or config endpoints
- Simple, predictable, testable
- Hardcode menu structure as:
  ```typescript
  const MENU_BY_ROLE: Record<Role, MenuItem[]> = {
    CLIENT: [
      { label: 'Catálogo', path: '/catalog', icon: 'ShoppingBag' },
      { label: 'Mi Carrito', path: '/cart', icon: 'Cart' },
      { label: 'Mis Pedidos', path: '/orders', icon: 'Package' },
      { label: 'Mi Perfil', path: '/profile', icon: 'User' },
    ],
    STOCK: [
      { label: 'Productos', path: '/stock/productos', icon: 'Package' },
      { label: 'Categorías', path: '/stock/categorias', icon: 'Folder' },
      { label: 'Ingredientes', path: '/stock/ingredientes', icon: 'Beaker' },
      { label: 'Stock', path: '/stock/stock', icon: 'Boxes' },
    ],
    PEDIDOS: [
      { label: 'Panel de Pedidos', path: '/pedidos/panel', icon: 'PackageCheck' },
    ],
    ADMIN: [
      // All options from all roles, plus:
      { label: 'Usuarios', path: '/admin/usuarios', icon: 'Users' },
      { label: 'Métricas', path: '/admin/metricas', icon: 'BarChart' },
      { label: 'Configuración', path: '/admin/settings', icon: 'Settings' },
    ],
  };
  ```

### Decision 4: Routing Structure
**Choice**: Nested routes with Layout as a route wrapper, not every page
**Rationale**:
- Cleaner structure: protected routes nested under `/app` parent route
- Layout renders once, outlet changes for each page
- Reduces re-renders and state resets

**Router Structure**:
```typescript
const router = [
  { path: '/', element: <Catalog /> }, // public
  { path: '/login', element: <LoginPage /> }, // public
  { path: '/register', element: <RegisterPage /> }, // public
  { path: '/unauthorized', element: <Unauthorized /> },
  {
    path: '/app',
    element: <ProtectedRoute><Layout /></ProtectedRoute>,
    children: [
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'orders', element: <ProtectedRoute roles={['CLIENT']}><OrdersList /></ProtectedRoute> },
      { path: 'stock/products', element: <ProtectedRoute roles={['ADMIN', 'STOCK']}><ProductsPage /></ProtectedRoute> },
      { path: 'admin/*', element: <ProtectedRoute roles={['ADMIN']}><AdminPanel /></ProtectedRoute> },
      // ... etc
    ]
  },
];
```

### Decision 5: Lazy Loading Modules
**Choice**: React.lazy() + Suspense for module pages (Products, Orders, Admin)
**Rationale**:
- Reduces initial bundle size by splitting feature chunks
- Only load when user actually visits that role-specific route
- Suspense shows a loading spinner while chunking

**Implementation**:
```typescript
const ProductsPage = React.lazy(() => import('@features/stock/pages/ProductsPage'));
const AdminPanel = React.lazy(() => import('@features/admin/pages/AdminPanel'));

// In route:
{
  path: 'stock/products',
  element: (
    <ProtectedRoute roles={['ADMIN', 'STOCK']}>
      <Suspense fallback={<PageSkeleton />}>
        <ProductsPage />
      </Suspense>
    </ProtectedRoute>
  )
}
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Deep nesting of ProtectedRoute HOCs** → readability suffers with multiple roles | Document that most routes will have simple single role. For complex auth logic, abstract into `requiresRole()` helper that returns boolean. |
| **Sidebar state loss on refresh** → user might get confused if sidebar was open and closes | Acceptable UX: sidebar reset is minor. If needed in future, can be persisted in Zustand. |
| **Menu hardcoding limits flexibility** → adding a new menu item requires code change | Intentional trade-off for now (MVP simplicity). Future: externalize to JSON config or API endpoint. |
| **Lazy loading adds initial load latency** → user sees loading spinner on first click to /stock/products | Mitigated by short loading times for small chunks. Suspense fallback (skeleton) improves perceived performance. |
| **Role-checking at UI level vs backend** → frontend can be bypassed (user could craft JWT) | Frontend guards are UX only. Backend MUST enforce authorization on every endpoint. This is not a replacement for backend /api/v1/products auth checks. |
| **Unauthenticated redirect loops** → if token refresh fails silently, user stuck in redirect loop | Protected by TanStack Query's 401 interceptor which calls logout() and redirects to /login on refresh failure. |

## Migration Plan

1. **Phase 1 (this sprint)**: Implement and test ProtectedRoute HOC, Header, Sidebar, Layout components in isolation
2. **Phase 2**: Integrate components into App.tsx router config (swap flat routes for nested structure)
3. **Phase 3**: Deploy and verify:
   - Unauthenticated user hits /app/* → redirects to /login ✓
   - CLIENT user sees CLIENT menu only ✓
   - STOCK user cannot access /app/admin/* → sees 403 ✓
   - Mobile sidebar toggle works ✓
4. **Rollback**: If issues arise, revert to flat router without layout wrapper (git revert). Keep ProtectedRoute for individual pages if needed.

## Open Questions

1. **Should unauthorized 403 page allow going back to previous route or default to dashboard?** → Proposal: default to dashboard (/app/dashboard) for consistency
2. **Should admin see all menu items for all roles or only admin items?** → Proposal: see all (full visibility) as specified in US-075
3. **Mobile breakpoint for sidebar collapse?** → Proposal: Tailwind's `md:` breakpoint (768px)
4. **Should menu items show icon + text or icon-only on mobile collapsed?** → Proposal: text hidden on collapsed, icon visible
