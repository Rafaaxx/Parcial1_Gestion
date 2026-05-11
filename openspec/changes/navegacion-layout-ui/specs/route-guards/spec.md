## ADDED Requirements

### Requirement: ProtectedRoute HOC validates authentication

The system SHALL implement a ProtectedRoute HOC that checks if the user is authenticated before rendering a component. If not authenticated, redirect to /login.

#### Scenario: Unauthenticated user is redirected to login
- **WHEN** an unauthenticated user navigates to a protected route (e.g., /app/orders)
- **THEN** ProtectedRoute checks isAuthenticated from authStore and finds it false
- **THEN** user is redirected to /login with replace=true

#### Scenario: Authenticated user can access protected route
- **WHEN** an authenticated user (with valid accessToken) navigates to /app/orders
- **THEN** ProtectedRoute checks isAuthenticated and finds it true
- **THEN** the protected component (OrdersList) is rendered

### Requirement: ProtectedRoute HOC validates role authorization

The system SHALL implement role-based authorization in ProtectedRoute. If a roles array is provided, the user MUST have at least one of the required roles.

#### Scenario: User with required role can access route
- **WHEN** a STOCK user navigates to /app/stock/products (requires roles=['ADMIN', 'STOCK'])
- **THEN** ProtectedRoute extracts user.roles from authStore and finds 'STOCK'
- **THEN** the route is allowed and component renders

#### Scenario: User without required role sees unauthorized page
- **WHEN** a CLIENT user navigates to /app/admin/users (requires roles=['ADMIN'])
- **THEN** ProtectedRoute checks roles and finds 'CLIENT' NOT in required roles
- **THEN** Unauthorized component is rendered (403 page)

#### Scenario: Admin can access all role-restricted routes
- **WHEN** an ADMIN user navigates to any protected route with roles=['ADMIN', 'STOCK'] or roles=['PEDIDOS']
- **THEN** ProtectedRoute checks roles and finds 'ADMIN' in required roles (ADMIN is superuser)
- **THEN** route is allowed

### Requirement: Routes are protected by default

The system SHALL define which routes are public (no auth required) and which are protected (auth + role required).

#### Scenario: Public routes are accessible without token
- **WHEN** an unauthenticated user navigates to /, /login, /register, or /catalog
- **THEN** no ProtectedRoute checks are triggered and page renders

#### Scenario: Protected routes require ProtectedRoute wrapper
- **WHEN** a route is under /app/* (e.g., /app/orders, /app/admin/users)
- **THEN** the route MUST be wrapped with ProtectedRoute HOC
- **THEN** unauthenticated or unauthorized access is blocked

### Requirement: Route guards support lazy loading

The system SHALL support lazy-loaded components in protected routes using React.lazy() and Suspense.

#### Scenario: Lazy-loaded component shows loading state
- **WHEN** user navigates to a lazy-loaded protected route (e.g., /app/admin/dashboard)
- **THEN** ProtectedRoute checks pass and Suspense fallback (skeleton/loader) appears
- **THEN** lazy component chunk is downloaded and rendered

### Requirement: Token expiration triggers redirect to login

The system SHALL detect when JWT access token expires and redirect user to /login. This is handled by the Axios interceptor, which triggers logout() in authStore when 401 is received.

#### Scenario: Expired token redirects to login
- **WHEN** user makes a request and receives HTTP 401 (token expired)
- **THEN** Axios interceptor detects 401 and calls authStore.logout()
- **THEN** user is redirected to /login
- **THEN** any in-flight requests are cancelled
