# Role-Based Navigation Architecture

## Overview

The application implements a comprehensive role-based navigation system with the following structure:

### User Roles

- **CLIENT**: End-user customers who can browse catalog and place orders
- **STOCK**: Warehouse/inventory managers who handle products and stock
- **PEDIDOS**: Order managers who process and manage customer orders
- **ADMIN**: System administrators with full access to all features

### Key Components

#### 1. **Layout** (`src/shared/components/Navigation/Layout.tsx`)

Main layout wrapper for authenticated routes. Renders:
- **Header**: Sticky top navigation with user info and logout
- **Sidebar**: Role-based menu navigation
- **Main Content**: Outlet for page content

```tsx
<ProtectedRoute requiredRoles={['ADMIN', 'STOCK', 'PEDIDOS', 'CLIENT']}>
  <Layout />  // Renders Header + Sidebar + Outlet
</ProtectedRoute>
```

#### 2. **ProtectedRoute** (`src/shared/routing/ProtectedRoute.tsx`)

HOC that enforces role-based access control:
- Checks if user is authenticated
- Validates user has required roles
- Redirects to `/login` if not authenticated
- Redirects to `/unauthorized` (403) if role mismatch

```tsx
<ProtectedRoute requiredRoles={['ADMIN', 'STOCK']}>
  <AdminPanel />
</ProtectedRoute>
```

#### 3. **Header** (`src/shared/components/Navigation/Header.tsx`)

Sticky header displaying:
- Application title
- User email/name and role badge
- Logout button
- Hamburger menu toggle (mobile)

#### 4. **Sidebar** (`src/shared/components/Navigation/Sidebar.tsx`)

Responsive sidebar with:
- Role-based menu items (from `menuConfig.ts`)
- User info section
- Active link highlighting
- Mobile-responsive (collapsible)

#### 5. **MenuItem** (`src/shared/components/Navigation/MenuItem.tsx`)

Individual menu item component with:
- Icon + label
- Link to route
- Active state indicator
- Collapsed icon-only mode (for future mobile optimization)

#### 6. **menuConfig** (`src/shared/components/Navigation/menuConfig.ts`)

Hardcoded menu structure by role:

```tsx
export const MENU_BY_ROLE: MenuItem[] = [
  // Available to ADMIN, STOCK, PEDIDOS
  { label: 'Dashboard', path: '/app/dashboard', icon: '📊', roles: ['ADMIN', 'STOCK', 'PEDIDOS'] },
  
  // CLIENT only
  { label: 'Catálogo', path: '/app/catalog', icon: '🛒', roles: ['CLIENT'] },
  { label: 'Carrito', path: '/app/cart', icon: '🛍️', roles: ['CLIENT'] },
  
  // ADMIN only
  { label: 'Usuarios', path: '/app/users', icon: '👥', roles: ['ADMIN'] },
  // ... more items
];
```

### Route Structure

Routes are organized under `/app` parent route with nested children:

```
/                                    (public)
  ├─ /login                          (public)
  ├─ /register                       (public)
  ├─ /catalog                        (public)
  ├─ /unauthorized                   (error page)
  ├─ /404                            (error page)
  └─ /app                            (protected - requires auth)
     ├─ /dashboard                   (requires ADMIN|STOCK|PEDIDOS)
     ├─ /catalog                     (CLIENT)
     ├─ /cart                        (CLIENT)
     ├─ /orders                      (CLIENT)
     ├─ /profile                     (CLIENT)
     ├─ /products                    (STOCK|ADMIN)
     ├─ /categories                  (STOCK|ADMIN)
     ├─ /ingredients                 (STOCK|ADMIN)
     ├─ /stock                       (STOCK|ADMIN)
     ├─ /orders-panel                (PEDIDOS)
     ├─ /users                       (ADMIN)
     ├─ /metrics                     (ADMIN)
     └─ /settings                    (ADMIN)
```

### Store Integration

#### Auth Store (`src/features/auth/store.ts`)

```tsx
const { user, isAuthenticated, setUser, logout } = useAuthStore();

// Check if user has specific role
userHasRole(user, ['ADMIN', 'STOCK'])
```

#### UI Store (`src/features/ui/store.ts`)

```tsx
const { sidebarOpen, setSidebarOpen } = useUIStore();

// Non-persisted sidebar state (resets on refresh)
```

### Usage Examples

#### Example 1: Protect a page for ADMIN only

```tsx
<Route
  path="admin-panel"
  element={
    <ProtectedRoute requiredRoles={['ADMIN']}>
      <AdminPanelPage />
    </ProtectedRoute>
  }
/>
```

#### Example 2: Add a menu item for a specific role

Edit `src/shared/components/Navigation/menuConfig.ts`:

```tsx
export const MENU_BY_ROLE: MenuItem[] = [
  // ... existing items
  {
    label: 'Reports',
    path: '/app/reports',
    icon: '📊',
    roles: ['ADMIN'],
  },
];
```

#### Example 3: Use auth data in a component

```tsx
import { useAuthStore, userHasRole } from '@/features/auth/store';

export function MyComponent() {
  const { user } = useAuthStore();
  
  if (userHasRole(user, ['ADMIN'])) {
    return <AdminFeature />;
  }
  
  return <UserFeature />;
}
```

### Testing

Tests are provided in:
- `src/shared/routing/ProtectedRoute.test.tsx`
- `src/shared/components/Navigation/Layout.test.tsx`
- `src/shared/components/Navigation/Sidebar.test.tsx`

Run tests:
```bash
npm test
npm run test:watch
```

### Styling

All components use **Tailwind CSS** with dark mode support:
- Header: `bg-white dark:bg-gray-900`
- Sidebar: `w-64`, responsive collapsible
- Mobile-first responsive design with `md:` breakpoint (768px)

### Error Pages

- **403 Unauthorized** (`src/pages/UnauthorizedPage.tsx`): User lacks required role
- **404 Not Found** (`src/pages/NotFoundPage.tsx`): Route doesn't exist

### Future Enhancements

- [ ] Externalize menu items to JSON/API for dynamic menu management
- [ ] Add permission-level granularity (not just roles)
- [ ] Persist sidebar state to localStorage
- [ ] Add breadcrumb navigation
- [ ] Add route transition animations
- [ ] Add skeleton loading states for lazy-loaded pages
