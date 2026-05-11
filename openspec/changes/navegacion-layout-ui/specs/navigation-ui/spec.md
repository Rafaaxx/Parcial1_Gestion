## ADDED Requirements

### Requirement: Navigation component renders role-specific menu items

The system SHALL render a Sidebar component that displays a list of navigation menu items based on the current user's role. Each role sees a distinct set of menu options.

#### Scenario: CLIENT role sees client menu
- **WHEN** a CLIENT user logs in and the Sidebar is rendered
- **THEN** the Sidebar displays: Catálogo, Mi Carrito, Mis Pedidos, Mi Perfil, Cerrar sesión

#### Scenario: STOCK role sees stock menu
- **WHEN** a STOCK user logs in and the Sidebar is rendered
- **THEN** the Sidebar displays: Productos, Categorías, Ingredientes, Stock, Cerrar sesión

#### Scenario: PEDIDOS role sees pedidos menu
- **WHEN** a PEDIDOS user logs in and the Sidebar is rendered
- **THEN** the Sidebar displays: Panel de Pedidos, Cerrar sesión

#### Scenario: ADMIN role sees all menu items
- **WHEN** an ADMIN user logs in and the Sidebar is rendered
- **THEN** the Sidebar displays: all items from CLIENT + STOCK + PEDIDOS menus, plus Usuarios, Métricas, Configuración, Cerrar sesión

### Requirement: Header component displays user info and logout button

The system SHALL display a Header component at the top of all protected pages showing the current user's name/email and a logout button.

#### Scenario: Header shows authenticated user info
- **WHEN** an authenticated user is on a protected page
- **THEN** the Header shows: user's email (or name), role badge, and Logout button

#### Scenario: Logout button clears auth state
- **WHEN** user clicks the Logout button
- **THEN** authStore.logout() is called, tokens are cleared, and user is redirected to /login

### Requirement: Navigation items are clickable links

The system SHALL make all menu items in Sidebar clickable links that navigate to their respective routes.

#### Scenario: Clicking menu item navigates to route
- **WHEN** user clicks a menu item (e.g., "Mis Pedidos")
- **THEN** react-router navigates to the corresponding route (e.g., /app/orders) and page content updates

### Requirement: Mobile responsive navigation

The system SHALL support responsive navigation on mobile devices with a collapsible sidebar.

#### Scenario: Sidebar collapses on mobile
- **WHEN** viewport width is less than 768px (md breakpoint)
- **THEN** Sidebar collapses to icon-only view and shows a hamburger toggle button

#### Scenario: Hamburger toggle expands sidebar
- **WHEN** user taps the hamburger menu on mobile
- **THEN** Sidebar expands to full width overlay and shows menu text

#### Scenario: Sidebar toggle state updates in uiStore
- **WHEN** user toggles the hamburger
- **THEN** uiStore.toggleSidebar() is called and UI re-renders with new state

### Requirement: Active menu item highlighting

The system SHALL highlight the currently active menu item based on the current route.

#### Scenario: Active link is visually highlighted
- **WHEN** user is on /app/orders
- **THEN** the "Mis Pedidos" menu item is highlighted (e.g., bg-blue-100 or bold text)
