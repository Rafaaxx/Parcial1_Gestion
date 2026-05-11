## ADDED Requirements

### Requirement: Feature-Sliced Design (FSD) Folder Structure
The system SHALL organize source code following Feature-Sliced Design principles with clear layer separation: shared, entities, features, pages, and app.

#### Scenario: Shared utilities are accessible from any feature
- **WHEN** a feature needs a common utility (e.g., formatPrice, useLocalStorage)
- **THEN** it imports from `src/shared/utils` or `src/shared/hooks`

#### Scenario: Feature-specific code stays in feature folder
- **WHEN** a feature (e.g., auth) has its own store, components, and services
- **THEN** they all live under `src/features/auth/` and are not imported into other features

#### Scenario: Page components reference features and entities
- **WHEN** a page (e.g., ProductDetail) renders
- **THEN** it imports from entities (Product model) and features (favorite toggle), not implementation details

### Requirement: Src Directory Structure
The system SHALL establish base directories for scalable organization:

```
src/
├── app/                 # App wrapper, root component, providers
├── pages/              # Page components (Login, Home, ProductDetail, etc.)
├── features/           # Feature modules (auth, cart, products, orders, etc.)
├── entities/           # Data models and types (User, Product, Order)
├── shared/             # Reusable utilities, hooks, UI components
│   ├── ui/            # UI atoms/molecules (Button, Card, Modal, Form)
│   ├── hooks/         # Custom hooks (useAPI, useLocalStorage, useAuth)
│   ├── utils/         # Helper functions (formatPrice, truncateText, etc.)
│   └── constants/     # App-wide constants (API_BASE_URL, ROLES, etc.)
└── config/            # App configuration, environment variables
```

#### Scenario: Navigate folder structure by feature
- **WHEN** a developer needs to work on shopping cart
- **THEN** they go to `src/features/cart/` and find all cart-related code there

#### Scenario: Find UI components
- **WHEN** a developer needs a Button component
- **THEN** they import from `src/shared/ui/Button`

#### Scenario: Find utilities
- **WHEN** a developer needs to format a price
- **THEN** they import `formatPrice` from `src/shared/utils/formatters`

### Requirement: TypeScript Path Aliases
The system SHALL configure TypeScript path aliases for shorter, cleaner imports.

#### Scenario: Use path alias in import
- **WHEN** a component imports from shared
- **THEN** it uses `import Button from '@/shared/ui/Button'` instead of `import Button from '../../../../shared/ui/Button'`

#### Scenario: Alias configuration in tsconfig.json
- **WHEN** the app is built
- **THEN** aliases are defined: `@/` → `src/`, `@shared` → `src/shared/`, `@features` → `src/features/`

### Requirement: Vite Configuration
The system SHALL configure Vite for fast development, HMR (Hot Module Replacement), and optimized production builds.

#### Scenario: HMR on file save
- **WHEN** a developer saves a component file
- **THEN** the browser automatically updates without full page reload

#### Scenario: Production build is optimized
- **WHEN** developer runs `npm run build`
- **THEN** output is minified, code-split, and optimized for performance

### Requirement: Public Assets Directory
The system SHALL provide a public folder for static assets (images, icons, favicon).

#### Scenario: Reference image in public folder
- **WHEN** a component renders an image from `public/images/logo.png`
- **THEN** it's accessible at `/images/logo.png` at runtime

### Requirement: Environment Configuration
The system SHALL support `.env` files for development and production configuration without secrets.

#### Scenario: Access environment variables
- **WHEN** code references `import.meta.env.VITE_API_BASE_URL`
- **THEN** it returns the value from `.env` file (e.g., `http://localhost:8000/api/v1`)

#### Scenario: .env.example template
- **WHEN** a new developer clones the repo
- **THEN** they copy `.env.example` to `.env` and update values locally

### Requirement: Package Manager Configuration
The system SHALL support both npm and pnpm with consistent lock files and dependency management.

#### Scenario: Install dependencies
- **WHEN** developer runs `npm install` or `pnpm install`
- **THEN** all dependencies from package.json are installed correctly

#### Scenario: Lock file consistency
- **WHEN** dependencies are installed
- **THEN** `package-lock.json` (npm) or `pnpm-lock.yaml` (pnpm) is generated and committed

### Requirement: Application Router with Lazy Loading
The system SHALL configure a client-side router with lazy-loaded pages for code splitting and optimal initial load time.

#### Scenario: Define all application routes
- **WHEN** the app starts
- **THEN** the following routes are registered:
  - `/` → HomePage
  - `/auth/login` → LoginPage
  - `/auth/register` → RegisterPage
  - `/productos` → ProductListPage
  - `/productos/:id` → ProductDetailPage
  - `/categorias/:id` → CategoryPage
  - `/carrito` → CartPage (protected, any authenticated user)
  - `/perfil` → ProfilePage (protected, any authenticated user)
  - `/admin` → AdminDashboard (protected, ADMIN only)
  - `/admin/productos` → AdminProducts (protected, ADMIN only)
  - `/admin/categorias` → AdminCategories (protected, ADMIN only)
  - `/admin/pedidos` → AdminOrders (protected, ADMIN only)
  - `/admin/usuarios` → AdminUsers (protected, ADMIN only)
  - `/admin/stock` → AdminStock (protected, ADMIN only)
  - `/403` → ForbiddenPage
  - `*` → NotFoundPage

#### Scenario: Pages are lazy-loaded
- **WHEN** a user navigates to a route
- **THEN** the page component is loaded via `React.lazy(() => import('@/pages/PageName'))` only when needed
- **THEN** code-split chunks are generated by Vite for each page

#### Scenario: ProtectedRoute wraps auth-required routes
- **WHEN** a route requires authentication (e.g., /carrito, /perfil)
- **THEN** it is nested inside a `<ProtectedRoute />` wrapper that checks auth state

#### Scenario: RoleGuard wraps admin routes
- **WHEN** a route requires ADMIN role (e.g., /admin/*)
- **THEN** it is nested inside `<ProtectedRoute requiredRoles={['ADMIN']} />`

### Requirement: App Root Composition
The app root (main.tsx + App.tsx) SHALL compose all providers and the router at the top level.

#### Scenario: Providers wrap the app
- **WHEN** the app renders
- **THEN** the component tree is: ErrorBoundary > QueryClientProvider > RouterProvider

#### Scenario: App.tsx is minimal
- **WHEN** App.tsx renders
- **THEN** it only renders `<RouterProvider router={router} />` — no other UI or logic
