# Architecture Guide

## Overview

Food Store Frontend uses **Feature-Sliced Design (FSD)** with **Zustand** for state management and **Tailwind CSS** for styling.

## Design Principles

### 1. Feature-Sliced Design (FSD)

FSD organizes code into four layers:

```
┌─────────────────────────────────┐
│  pages                          │ <- Page compositions
├─────────────────────────────────┤
│  features                       │ <- Feature logic
├─────────────────────────────────┤
│  entities                       │ <- Data models
├─────────────────────────────────┤
│  shared                         │ <- Reusable utilities
└─────────────────────────────────┘
```

#### App Layer
- Root component with providers
- Global theme setup
- Exception boundaries

#### Pages Layer
- Page components (HomePage, ProductDetail, CheckoutPage)
- Combine features and layouts
- Handle routing (in CHANGE-02)

#### Features Layer
Each feature is self-contained:
```
features/
├── auth/
│   ├── store.ts        # Zustand store
│   ├── types.ts        # TypeScript interfaces
│   ├── components/     # Feature-specific UI
│   └── api/           # API calls (future)
├── cart/
│   ├── types.ts
│   ├── components/
│   └── store.ts
└── ui/
    ├── store.ts       # Theme, toasts
    └── types.ts
```

**Rules:**
- Features can depend on shared code
- Features CAN depend on entities
- Features CANNOT depend on other features (prevents circular dependencies)
- Feature exports go through `index.ts` (barrel export)

#### Entities Layer
- Data models: `User`, `Product`, `Order`
- Types and interfaces
- No business logic
- Reusable across features

#### Shared Layer
- UI components (Button, Card, Modal)
- Custom hooks (useAuth, useTheme)
- Utilities (formatters, validators)
- HTTP client
- Store factory
- Constants

### 2. State Management (Zustand)

**Why Zustand?**
- Lightweight (~2KB)
- First-class TypeScript support
- Hooks-based API
- No boilerplate

**Store Structure:**
```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useMyStore = create<MyState>(
  persist(
    (set, get) => ({
      value: 'initial',
      setValue: (val) => set({ value: val }),
    }),
    { name: 'my-store-key' }
  )
)
```

**Patterns:**
- Stores live in `features/*/store.ts`
- Selectors use hooks: `useAuthStore(state => state.user)`
- Custom hooks wrap stores: `useAuth()` exports auth functionality
- Persistence enabled for UI state (theme, sidebar)

### 3. Component Design

Components are organized into:

#### Shared UI Components (`src/shared/ui/`)
- Presentation-only components
- No business logic
- Fully typed with TypeScript
- Accept props for configuration
- Example: `Button`, `Card`, `Modal`

**Example:**
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
  isLoading?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', isLoading, ...props }, ref) => {
    return <button ref={ref} {...props}>{isLoading ? '...' : props.children}</button>
  }
)
```

#### Feature Components (`src/features/*/components/`)
- Logic-heavy components
- Connect to stores and APIs
- Composed from shared UI components
- Example: `LoginForm`, `CartWidget`

### 4. Styling with Tailwind

**Approach:**
- Utility-first CSS with Tailwind
- Dark mode with `dark:` prefix
- Theme variables in `tailwind.config.ts`
- Component-level Tailwind classes

**Dark Mode:**
```typescript
// Apply theme to html element
document.documentElement.classList.add('dark')

// Use in components
<div className="bg-white dark:bg-gray-900">
  <p className="text-gray-900 dark:text-gray-50">Text</p>
</div>
```

### 5. HTTP Client (Axios)

Pre-configured interceptors:

**Request Interceptor:**
- Adds `Authorization: Bearer <token>` header
- Called before each request

**Response Interceptor:**
- Logs requests/responses in debug mode
- Handles 401 Unauthorized:
  - Calls refresh endpoint (CHANGE-01)
  - Updates token in auth store
  - Retries original request
  - Falls back to logout if refresh fails

**Usage:**
```typescript
import { apiClient } from '@/shared/http'

const { data } = await apiClient.get('/productos')
const { data } = await apiClient.post('/auth/login', { email, password })
```

### 6. Custom Hooks

Hooks provide convenient access to features:

```typescript
// useAuth.ts
export function useAuth() {
  return {
    user: useAuthStore(s => s.user),
    token: useAuthStore(s => s.token),
    logout: useAuthStore(s => s.logout),
  }
}

// In components
const { user, logout } = useAuth()
```

**Benefits:**
- Single source of truth for related functionality
- Easy to test
- Clear API surface

## Data Flow

```
┌─────────────┐
│  Component  │ <- (useAuth, useTheme)
└──────┬──────┘
       │
       v
┌─────────────────┐
│  Custom Hooks   │ <- useAuthStore(selector)
└──────┬──────────┘
       │
       v
┌─────────────────┐
│  Zustand Store  │ <- (get, set)
└──────┬──────────┘
       │
       v
┌─────────────────┐
│  localStorage   │ (persist middleware)
└─────────────────┘
```

**For API calls:**
```
┌─────────────┐
│  Component  │ <-- Click "Load Products"
└──────┬──────┘
       │
       v
┌──────────────────────┐
│  Feature Component   │ <-- Call apiClient.get()
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│  HTTP Interceptor    │ <-- Add token header
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│  Backend API         │ <-- /productos endpoint
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│  Response Interceptor│ <-- Log, handle errors
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│  Update Store        │ <-- setProducts([...])
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│  Component Re-render │ <-- useProductsStore selector
└──────────────────────┘
```

## File Naming Conventions

- **Components**: `PascalCase.tsx` (e.g., `Button.tsx`, `LoginForm.tsx`)
- **Stores**: `camelCase.ts` with export named `use*Store` (e.g., `authStore.ts` exports `useAuthStore`)
- **Utilities**: `camelCase.ts` (e.g., `formatters.ts`, `validators.ts`)
- **Types**: `camelCase.ts` (e.g., `auth.types.ts`, or inline in store files)
- **Hooks**: `use*.ts` (e.g., `useAuth.ts`, `useLocalStorage.ts`)

## Import Paths

Always use path aliases:

✅ **Good:**
```typescript
import { Button } from '@/shared/ui'
import { useAuth } from '@/shared/hooks'
import { formatPrice } from '@/shared/utils'
```

❌ **Bad:**
```typescript
import { Button } from '../../../shared/ui/Button'
```

## Type Safety

- **Strict TypeScript mode enabled**
- All components have full type definitions
- Store state is typed with interfaces
- Props interfaces extend React types for compatibility

## Testing Strategy (CHANGE-16)

- Unit tests for utilities and hooks
- Integration tests for features
- E2E tests for critical flows
- Tests colocated with features: `features/auth/__tests__/`

## Performance Optimization

- **Code splitting**: Each route lazy-loaded (CHANGE-02)
- **Memoization**: Use `React.memo()` for heavy components
- **Selectors**: Zustand selectors prevent unnecessary re-renders
- **CSS**: Tailwind purges unused classes in build
- **Images**: Optimize before adding to public/

## Common Patterns

### Feature Store with Actions

```typescript
export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  addItem: (item) => set(state => ({
    items: [...state.items, item]
  })),
  getTotalPrice: () => {
    const { items } = get()
    return items.reduce((sum, item) => sum + item.price, 0)
  }
}))
```

### Component with Store Integration

```typescript
export const CartWidget: React.FC = () => {
  const items = useCartStore(s => s.items)
  const total = useCartStore(s => s.getTotalPrice())
  
  return <div>Cart ({items.length}): ${total}</div>
}
```

### Error Handling

```typescript
try {
  const data = await apiClient.get('/products')
  useUIStore.setState({
    toast: { type: 'success', message: 'Loaded!' }
  })
} catch (error) {
  useUIStore.setState({
    toast: { type: 'error', message: 'Failed to load' }
  })
}
```

## Debugging

### Enable Debug Mode
```env
VITE_DEBUG=true
```

This enables:
- HTTP request/response logging to console
- Zustand devtools support
- Detailed error messages

### Browser DevTools

- Open browser console to see API logs
- Inspect HTML to verify Tailwind classes
- Network tab to monitor API calls

## Migration Guide

Moving code to FSD structure:

1. **Identify the feature** (e.g., "user authentication")
2. **Create feature folder** at `src/features/<feature-name>`
3. **Extract store** to `store.ts`
4. **Extract types** to `types.ts`
5. **Move components** to `components/`
6. **Create barrel export** at `index.ts`
7. **Update imports** across the app

## Resources

- [Zustand Docs](https://github.com/pmndrs/zustand)
- [Tailwind CSS Docs](https://tailwindcss.com/)
- [Feature-Sliced Design](https://feature-sliced.design/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
