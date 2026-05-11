## ADDED Requirements

### Requirement: Store Factory Pattern
The system SHALL provide a factory function to create typed Zustand stores with consistent behavior, TypeScript generics support, and optional devtools integration.

#### Scenario: Create an auth store
- **WHEN** a developer calls `createStore<AuthState>({ user: null, token: null })`
- **THEN** the system returns a usable Zustand hook with typed state, getters, and setters

#### Scenario: Store has selector hooks
- **WHEN** a consumer calls a selector like `useAuthStore(state => state.user)`
- **THEN** the system returns only the selected state slice and re-renders only on that slice's changes

### Requirement: Auth Store Implementation
The system SHALL provide an auth store for managing user identity, tokens, and authentication state across the app.

#### Scenario: Initialize auth store
- **WHEN** the app starts
- **THEN** the auth store initializes with `{ user: null, token: null, refreshToken: null }`

#### Scenario: Store and retrieve user
- **WHEN** user logs in successfully
- **THEN** auth store updates `user`, `token`, and `refreshToken` fields

#### Scenario: Clear auth on logout
- **WHEN** user clicks logout
- **THEN** auth store resets all fields to null

### Requirement: UI Store Implementation
The system SHALL provide a UI store for managing global UI state: modals, toasts, theme, sidebar visibility.

#### Scenario: Toggle theme
- **WHEN** user clicks dark mode toggle
- **THEN** UI store updates `theme` from 'light' to 'dark' (or vice versa)

#### Scenario: Show notification toast
- **WHEN** an API request completes
- **THEN** app can call `useUIStore.setState({ toast: { type: 'success', message: '...' } })`

#### Scenario: Theme persists across sessions
- **WHEN** user sets dark mode and closes the browser
- **THEN** on return, dark mode is still active (persisted to localStorage)

### Requirement: Cart Store Signature (for CHANGE-08)
The system SHALL define the cart store interface (not fully implement until CHANGE-08), ensuring other changes can reference it.

#### Scenario: Cart store type is available
- **WHEN** CHANGE-08 starts implementing shopping cart
- **THEN** it imports the `CartState` type and knows the expected structure: `{ items: CartItem[], addItem(), removeItem(), clearCart() }`

### Requirement: Store Composition with Multiple Stores
The system SHALL support composing multiple stores without conflicts, each scoped to its own domain.

#### Scenario: Auth and UI stores coexist
- **WHEN** the app renders
- **THEN** `useAuthStore` and `useUIStore` work independently; updating auth doesn't trigger UI re-renders and vice versa

### Requirement: Devtools Support (Optional)
The system MAY provide optional integration with Zustand devtools for debugging store state during development.

#### Scenario: Developer enables devtools
- **WHEN** developer sets `VITE_DEBUG=true` in .env
- **THEN** stores register with Zustand devtools for time-travel inspection (optional, not required)

### Requirement: Auth Store Persist Middleware
The auth store SHALL use Zustand's `persist()` middleware to survive page reloads, with `partialize` limiting persistence to non-sensitive fields only.

#### Scenario: Persist token across page reloads
- **WHEN** user refreshes the page
- **THEN** auth store rehydrates `token` and `refreshToken` from localStorage (not user data)

#### Scenario: partialize excludes user data from storage
- **WHEN** auth state is persisted to localStorage
- **THEN** only `token` and `refreshToken` are saved — `user` and sensitive fields are excluded

#### Scenario: rehydrated flag prevents flash of unauthenticated state
- **WHEN** the store finishes rehydrating from localStorage
- **THEN** `rehydrated` is set to `true` via `onRehydrateStorage` callback

### Requirement: Auth Store hasRole() Method
The auth store SHALL provide a `hasRole(role)` method that checks if the current user has a specific role.

#### Scenario: Check user role
- **WHEN** `hasRole('ADMIN')` is called and user has ADMIN role
- **THEN** it returns `true`

#### Scenario: Check role when not authenticated
- **WHEN** `hasRole('ADMIN')` is called and user is null
- **THEN** it returns `false`

#### Scenario: User.roles is typed array
- **WHEN** auth store initializes user data
- **THEN** `user.roles` is of type `Role[]` where `Role = 'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT'`
