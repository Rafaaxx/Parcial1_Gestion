## 1. Setup and Project Structure

- [ ] 1.1 Create directory structure: `src/shared/components/Navigation/`, `src/shared/stores/`, `src/pages/` for new pages
- [ ] 1.2 Verify authStore has user.roles array persisted and isAuthenticated selector
- [ ] 1.3 Verify uiStore exists with sidebarOpen state and toggleSidebar() action
- [ ] 1.4 Install or verify React Router v6 is configured (react-router-dom already in dependencies)

## 2. Core Navigation Components

- [ ] 2.1 Create `src/shared/components/Navigation/Header.tsx` component
  - Displays user email/name, role badge, logout button
  - Hamburger menu toggle on mobile
  - Responsive styling (Tailwind)
- [ ] 2.2 Create `src/shared/components/Navigation/Sidebar.tsx` component
  - Renders MENU_BY_ROLE based on current user roles
  - Displays menu items as Link components
  - Shows active link highlighting
  - Responsive (collapsed to icons on mobile)
- [ ] 2.3 Create `src/shared/components/Navigation/MenuItem.tsx` component (optional, reusable)
  - Icon + label
  - Hover state
  - Active state indicator
- [ ] 2.4 Create MENU_BY_ROLE constant mapping roles to menu items
  - CLIENT: Catálogo, Carrito, Mis Pedidos, Mi Perfil, Cerrar sesión
  - STOCK: Productos, Categorías, Ingredientes, Stock, Cerrar sesión
  - PEDIDOS: Panel de Pedidos, Cerrar sesión
  - ADMIN: All items + Usuarios, Métricas, Configuración, Cerrar sesión

## 3. Layout and Route Guards

- [ ] 3.1 Create `src/shared/components/Navigation/Layout.tsx` component
  - Renders Header + Sidebar + main content (Outlet)
  - Responsive grid/flex layout
  - Manages sidebar toggle state via uiStore
- [ ] 3.2 Create `src/shared/components/Navigation/ProtectedRoute.tsx` HOC
  - Checks isAuthenticated
  - Checks required roles if provided
  - Redirects to /login if not authenticated
  - Renders Unauthorized page if role mismatch
- [ ] 3.3 Create `src/pages/UnauthorizedPage.tsx` (403 error page)
  - Displays "403 - Forbidden" message
  - Provides "Go to Dashboard" button
  - Provides "Go Back" button
  - Responsive styling

## 4. Router Configuration

- [ ] 4.1 Update `src/app/App.tsx` or main router file
  - Restructure routes from flat to nested
  - Create /app parent route with Layout wrapper
  - Move protected pages under /app routes
  - Define public routes: /, /login, /register, /catalog, /unauthorized
  - Add ProtectedRoute HOC to each protected route with required roles
- [ ] 4.2 Implement route lazy loading for heavy pages
  - Use React.lazy() for: ProductsPage, AdminPanel, etc.
  - Wrap with Suspense with PageSkeleton fallback
- [ ] 4.3 Add NotFound (404) page for unmatched routes
  - Basic 404 component with link to home

## 5. Styling and Responsive Design

- [ ] 5.1 Apply Tailwind CSS utility classes to Header
  - Background color (e.g., bg-blue-600), text color, padding
  - User info section (text-right)
  - Logout button (button styling)
- [ ] 5.2 Apply Tailwind CSS to Sidebar
  - Background, border, spacing
  - Menu item hover and active states
  - Icon + text layout
  - Collapsed icon-only layout on mobile (md:)
- [ ] 5.3 Apply responsive design patterns
  - Header: full width, fixed or sticky
  - Sidebar: flex shrink/grow, responsive width changes
  - Main content: flex grow, padding adjustments
  - Breakpoint md (768px) for mobile/desktop toggle
- [ ] 5.4 Add hamburger menu icon on mobile Header
  - Show/hide based on sidebar toggle state
  - Use icon library (react-icons or custom SVG)

## 6. Integration with Zustand Stores

- [ ] 6.1 Ensure authStore exports:
  - useAuthStore.getState() for ProtectedRoute
  - Selectors: isAuthenticated, user, user.roles
- [ ] 6.2 Ensure uiStore has:
  - sidebarOpen boolean state
  - toggleSidebar() action
  - useUIStore() hook for components
- [ ] 6.3 Test store integration:
  - Verify logout() in authStore clears tokens and redirects
  - Verify toggleSidebar() updates UI state

## 7. TypeScript Types and Validation

- [ ] 7.1 Create types for navigation:
  - MenuItem interface: { label, path, icon, roles? }
  - Define Role union type (CLIENT | STOCK | PEDIDOS | ADMIN)
- [ ] 7.2 Ensure ProtectedRoute is properly typed
  - children: ReactNode
  - roles?: string[]
- [ ] 7.3 Run `tsc --noEmit` to check for TypeScript errors
- [ ] 7.4 Ensure strict: true in tsconfig.json and no `any` types in new components

## 8. Testing

- [ ] 8.1 Create tests for ProtectedRoute HOC
  - Test: renders children when authenticated with correct role
  - Test: redirects to /login when not authenticated
  - Test: renders Unauthorized when role missing
- [ ] 8.2 Create tests for Sidebar component
  - Test: renders correct menu items for each role
  - Test: clicking menu item navigates to correct route
  - Test: active link is highlighted
- [ ] 8.3 Create tests for Header component
  - Test: displays user email
  - Test: logout button calls authStore.logout()
- [ ] 8.4 Create tests for Layout component
  - Test: renders Header + Sidebar + Outlet
  - Test: Sidebar toggle works
  - Test: responsive behavior on different viewports

## 9. Documentation and Quality Assurance

- [ ] 9.1 Add JSDoc comments to all exported components
  - Explain props, return type, example usage
- [ ] 9.2 Update README.md with navigation structure
  - Document protected vs public routes
  - Document role requirements
- [ ] 9.3 Run linter and formatter
  - `npm run lint` (ESLint)
  - `npm run format` (Prettier)
- [ ] 9.4 Perform manual testing
  - Test each role's menu (CLIENT, STOCK, PEDIDOS, ADMIN)
  - Test unauthenticated redirect
  - Test role-based unauthorized access
  - Test mobile responsiveness (DevTools)
  - Test logout flow

## 10. Integration and Cleanup

- [ ] 10.1 Commit changes with conventional commit: `feat(navigation): add role-based navigation and layout`
- [ ] 10.2 Remove any old/temporary routing code
- [ ] 10.3 Verify no TypeScript errors or ESLint warnings
- [ ] 10.4 Test end-to-end flow:
  - Login as different roles
  - Verify correct menu appears
  - Verify protected routes work
  - Verify unauthorized access shows 403
  - Verify mobile responsive behavior
