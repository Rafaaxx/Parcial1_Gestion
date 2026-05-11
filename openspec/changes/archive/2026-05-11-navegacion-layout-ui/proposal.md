## Why

Currently, Food Store has no unified frontend navigation system. Different user roles (ADMIN, STOCK, PEDIDOS, CLIENT) require distinct menu options and access patterns. Without a navigation layer adapted by role, users see either nothing or everything—leading to confusion, accidental access, or poor UX. US-075 and US-076 require a role-aware navigation system with protected routes and clear visual hierarchy.

This change establishes the navigation backbone: a header/sidebar component system that adapts to user roles and a routing guard system that enforces authorization at the UI level before users hit protected endpoints.

## What Changes

- **New**: Role-based navigation menu with distinct options per role (CLIENT → Catalog, Cart, Orders, Profile; STOCK → Products, Categories, Ingredients, Stock; PEDIDOS → Order Panel; ADMIN → everything + Users, Metrics, Settings)
- **New**: ProtectedRoute HOC wrapper that guards routes by authentication and role
- **New**: Navigation layout wrapper that renders header + sidebar + content area
- **New**: Route guards that redirect unauthenticated users to login
- **New**: Public routes list (Catalog, Login, Register) accessible without auth
- **New**: Role-aware guards that prevent role mismatch access (403 UI placeholder)
- **Modified**: App root routing structure to incorporate layout + guards

## Capabilities

### New Capabilities

- `navigation-ui`: Header/Sidebar components that render menu items based on current user's role(s). Menu options: CLIENT sees Catalog/Cart/Orders/Profile; STOCK sees Products/Categories/Ingredients/Stock; PEDIDOS sees Order Panel; ADMIN sees all + Admin features.
- `route-guards`: ProtectedRoute HOC and route guards that validate authentication (redirects to /login if no token) and role authorization (shows 403 or redirects to /unauthorized if role mismatch). Includes lazy loading of module-specific routes.
- `layout-wrapper`: Main layout component wrapping all protected pages with header + sidebar + main content area. Responsive design with sidebar toggle on mobile.
- `unauthorized-page`: 403 Forbidden page shown when user lacks required role. Includes explanation and link back to dashboard.

### Modified Capabilities

(none)

## Impact

**Affected Frontend Modules**:
- `src/app/`: Main App.tsx router structure
- `src/shared/components/`: New Navigation, Header, Sidebar, ProtectedRoute components
- `src/pages/`: All page components now wrapped with layout
- `src/entities/auth/`: authStore selector methods (hasRole, isAuthenticated)
- `src/shared/stores/authStore.ts`: Ensure role array is persisted

**Affected Hooks/Dependencies**:
- Uses `useAuthStore(s => s.user.roles)` and `useAuthStore(s => s.isAuthenticated)`
- Uses `useNavigate()` from react-router-dom for redirects
- Uses lazy `React.lazy()` + Suspense for code splitting by feature

**No Backend Changes**: Navigation is pure frontend; no API modifications.

**Breaking Changes**: App root routing changes from flat routes to nested protected routes with layout wrapper. All protected pages now render inside layout (not a breaking change to existing APIs, but UX flow changes).

**Rollback Plan**: If issues arise, revert to flat route structure without layout wrapper. Guards can be conditionally disabled via feature flag in Zustand uiStore.
