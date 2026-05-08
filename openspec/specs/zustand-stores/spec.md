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
