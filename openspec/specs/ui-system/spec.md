## ADDED Requirements

### Requirement: Button Component
The system SHALL provide a reusable Button component with variants: primary, secondary, danger, and states: default, loading, disabled.

#### Scenario: Render primary button
- **WHEN** developer renders `<Button variant="primary">Click Me</Button>`
- **THEN** a styled button appears with primary theme color

#### Scenario: Button has loading state
- **WHEN** developer renders `<Button isLoading>Submit</Button>`
- **THEN** button shows spinner, text is hidden, click is disabled

#### Scenario: Button can be disabled
- **WHEN** developer renders `<Button disabled>Unavailable</Button>`
- **THEN** button is grayed out and unclickable

### Requirement: Card Component
The system SHALL provide a reusable Card component for content containers with padding, border, and shadow.

#### Scenario: Render basic card
- **WHEN** developer renders `<Card><h2>Title</h2><p>Content</p></Card>`
- **THEN** content is wrapped in a styled container with padding and border

#### Scenario: Card supports interactive hover effect
- **WHEN** user hovers over a Card with `interactive` prop
- **THEN** the card shadow increases (elevation effect)

### Requirement: Modal Component
The system SHALL provide a Modal dialog for overlays, confirmations, and forms.

#### Scenario: Open and close modal
- **WHEN** developer renders `<Modal isOpen={true} onClose={handler}><p>Content</p></Modal>`
- **THEN** a modal appears with backdrop, content, and close button

#### Scenario: Modal with title and actions
- **WHEN** developer renders `<Modal title="Confirm" actions={[okBtn, cancelBtn]}>`
- **THEN** modal displays title at top and action buttons at bottom

### Requirement: Form Components (Input, Textarea, Select)
The system SHALL provide form input components with validation styling, labels, and error messages.

#### Scenario: Render text input with label
- **WHEN** developer renders `<Input label="Email" type="email" />`
- **THEN** a labeled input field appears

#### Scenario: Show validation error
- **WHEN** developer renders `<Input error="Email is required" />`
- **THEN** input border turns red and error message appears below

#### Scenario: Select dropdown
- **WHEN** developer renders `<Select options={[{label: 'A', value: 1}]} />`
- **THEN** a dropdown appears with options

### Requirement: Tailwind CSS Theme System
The system SHALL use Tailwind CSS with custom theme variables for colors, spacing, and typography.

#### Scenario: Light mode colors
- **WHEN** user is in light mode
- **THEN** background is white, text is dark gray, accent is brand blue

#### Scenario: Dark mode colors
- **WHEN** user is in dark mode
- **THEN** background is dark gray, text is light, accent is bright blue

#### Scenario: Theme switching
- **WHEN** user clicks theme toggle
- **THEN** the `<html>` element class changes from `light` to `dark` (or vice versa)
- **THEN** all components automatically adapt their colors via Tailwind's `dark:` prefix

### Requirement: Responsive Design
The system SHALL support responsive layout using Tailwind breakpoints: mobile, tablet, desktop.

#### Scenario: Grid layout responsive
- **WHEN** component renders on mobile (< 640px)
- **THEN** layout is single-column
- **WHEN** component renders on tablet (640px - 1024px)
- **THEN** layout is 2 columns
- **WHEN** component renders on desktop (> 1024px)
- **THEN** layout is 3 columns

### Requirement: Alert / Toast Notification Component
The system SHALL provide dismissible toast notifications for success, error, warning, and info messages.

#### Scenario: Show success toast
- **WHEN** developer calls `showToast({ type: 'success', message: 'Saved!' })`
- **THEN** a green toast appears in top-right corner and auto-dismisses after 3 seconds

#### Scenario: Dismiss manual toast
- **WHEN** user clicks X button on toast
- **THEN** toast disappears immediately

### Requirement: Loading Skeleton
The system SHALL provide a skeleton/loader component for displaying content placeholders during data fetching.

#### Scenario: Show loading skeleton
- **WHEN** data is being fetched
- **THEN** skeleton appears as gray shimmer placeholders matching the final layout

### Requirement: AppLayout — Main Application Shell
The system SHALL provide an AppLayout component that serves as the main application shell with Header, Breadcrumbs, content area, and Footer.

#### Scenario: AppLayout renders with all sections
- **WHEN** any page renders inside the layout
- **THEN** the layout shows: Header (sticky, top), Breadcrumbs, main content area (Suspense + Outlet), Footer (bottom)

#### Scenario: Header includes navigation and user controls
- **WHEN** the layout renders
- **THEN** Header contains: Logo (links to /), NavMenu (desktop), CartBadge, UserDropdown (if authenticated) or Login link (if not), Theme toggle, Mobile hamburger button

#### Scenario: Suspense shows skeleton fallback
- **WHEN** a lazy-loaded page is loading
- **THEN** React.Suspense shows skeleton placeholders (Skeleton component) instead of full page flash

### Requirement: NavMenu — Role-Based Navigation
The system SHALL provide a NavMenu component that displays navigation items filtered by user role.

#### Scenario: Render desktop navigation
- **WHEN** user is on desktop (> 768px)
- **THEN** NavMenu displays inline horizontal links with active state highlighting

#### Scenario: Render mobile hamburger menu
- **WHEN** user is on mobile (< 768px)
- **THEN** NavMenu receives `isMobile` prop and renders inside a slide-in panel with overlay

#### Scenario: Filter menu items by role
- **WHEN** user does not have ADMIN role
- **THEN** admin-only menu items (Dashboard, Products, Categories, Orders, Users, Stock) are hidden

#### Scenario: Active link highlighting
- **WHEN** a NavLink matches the current route
- **THEN** it has an active style (primary color, bold or underline)

### Requirement: Breadcrumbs — Navigation Trail
The system SHALL provide a Breadcrumbs component that shows the current page path as a navigable trail.

#### Scenario: Show breadcrumb trail
- **WHEN** user navigates to /productos/123
- **THEN** breadcrumbs show: Inicio > Productos > [Product Name]
- **THEN** each segment is clickable except the last (current page)

#### Scenario: Breadcrumbs use path matching
- **WHEN** the route changes
- **THEN** breadcrumbs automatically derive segments from the current pathname and route metadata

### Requirement: Footer — Application Footer
The system SHALL provide a Footer component displayed at the bottom of every page.

#### Scenario: Footer renders at page bottom
- **WHEN** the AppLayout renders
- **THEN** Footer appears at the bottom with copyright, links, and branding

### Requirement: CartBadge — Cart Icon with Count
The system SHALL provide a CartBadge component showing the cart icon with current item count.

#### Scenario: Show cart icon with count
- **WHEN** cart has items
- **THEN** CartBadge shows a shopping cart icon with a badge overlay displaying the item count

#### Scenario: CartBadge links to cart page
- **WHEN** user clicks the cart badge
- **THEN** they are navigated to /carrito

### Requirement: UserDropdown — User Menu
The system SHALL provide a UserDropdown component for authenticated user actions.

#### Scenario: Show user menu
- **WHEN** user is authenticated and clicks their name/avatar
- **THEN** a dropdown menu appears with: Perfil link, Cerrar Sesión button

#### Scenario: Logout clears auth state
- **WHEN** user clicks Cerrar Sesión
- **THEN** auth store is cleared and user is redirected to home

### Requirement: ProtectedRoute — Authentication Guard
The system SHALL provide a ProtectedRoute component that wraps routes requiring authentication.

#### Scenario: Redirect to login when not authenticated
- **WHEN** an unauthenticated user visits a protected route
- **THEN** they are redirected to /auth/login?redirect=<original_path>

#### Scenario: Wait for rehydrated before checking auth
- **WHEN** the auth store has not finished rehydrating
- **THEN** ProtectedRoute shows a loading skeleton instead of prematurely redirecting

#### Scenario: Show 403 when wrong role
- **WHEN** an authenticated user lacks the required role
- **THEN** a ForbiddenAccess message is displayed (not a redirect)

### Requirement: ErrorBoundary — Catch Render Errors
The system SHALL provide an ErrorBoundary class component that catches JavaScript errors in the component tree.

#### Scenario: Show fallback UI on error
- **WHEN** a component throws during rendering
- **THEN** ErrorBoundary shows a fallback UI with error message and "Reintentar" button

#### Scenario: Retry resets error state
- **WHEN** user clicks "Reintentar"
- **THEN** ErrorBoundary resets `hasError` state via `setState({ hasError: false })` and re-renders children

#### Scenario: DEV mode shows error details
- **WHEN** `import.meta.env.DEV` is true
- **THEN** ErrorBoundary also displays the error stack trace for debugging
