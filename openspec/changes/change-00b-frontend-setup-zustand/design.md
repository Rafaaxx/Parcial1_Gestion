## Context

CHANGE-00a successfully set up the FastAPI backend with async SQLAlchemy, UoW pattern, and proper exception handling. The backend is ready to serve API requests at `http://localhost:8000/api/v1/*`.

CHANGE-00b must establish a parallel frontend foundation that can consume this API. The frontend needs:
1. Modern React 19 with TypeScript for type safety
2. Zustand for lightweight, functional state management (vs Redux which is overkill for this project)
3. HTTP client integration with automatic token handling for future authentication
4. FSD (Feature-Sliced Design) architecture for scalability and team collaboration
5. Tailwind CSS for rapid UI development with theming support
6. Development tooling with Vite for fast HMR and builds

The frontend will live in `frontend/` alongside backend, both monorepo-style within the Git repo.

## Goals / Non-Goals

**Goals:**
- Initialize React 19 + TypeScript project with Vite bundler
- Set up Zustand with reusable store factory functions for type-safe global state
- Create HTTP client (Axios) with request/response interceptors for API integration
- Implement FSD folder structure for scalable component organization
- Add Tailwind CSS with theme system (light/dark mode foundation)
- Create base component library (Button, Card, Modal, Form) with consistent styling
- Set up linting (ESLint) and formatting (Prettier) with Git hooks (Husky)
- Enable TypeScript strict mode and path aliases for imports

**Non-Goals:**
- NOT implementing actual authentication UI yet (CHANGE-01 does that)
- NOT building real pages/routes yet (defer to CHANGE-02)
- NOT setting up testing framework (defer to CHANGE-16)
- NOT implementing shopping cart state (defer to CHANGE-08)
- NOT configuring CI/CD pipelines (defer to CHANGE-16)

## Decisions

### 1. Zustand over Redux / MobX / Jotai
**Why:** Zustand is lightweight (~2KB), has first-class TypeScript support, and is perfect for mid-scale apps. Redux is overkill; Jotai is more granular. Zustand's functional approach with hooks matches React 19 best practices.

**Alternatives considered:**
- Redux: More boilerplate, time-consuming for this project scope
- MobX: Less predictable data flow, harder to debug
- Context API: Not suitable for frequent updates (shopping cart, filters)

**Decision:** Zustand is chosen.

### 2. Vite over Next.js / Create React App
**Why:** Vite has 10x faster HMR than CRA, no build overhead, and is the standard for modern React. Next.js is unnecessary here (no SSR required for Food Store).

**Alternatives considered:**
- Next.js: Adds complexity, SSR overhead not needed for SPA
- CRA: Slow startup, bloated dependencies

**Decision:** Vite is chosen.

### 3. Tailwind CSS + styled-components for UI
**Why:** Tailwind provides rapid development with utility classes, excellent theme support for dark mode. Paired with styled-components for complex component-scoped styles.

**Alternatives considered:**
- CSS Modules: Verbose, no theming out of box
- Emotion: Same as styled-components, less mature community

**Decision:** Tailwind + styled-components hybrid approach.

### 4. Axios HTTP Client with Interceptors
**Why:** Axios provides request/response interceptors for automatic token refresh (CHANGE-01), error handling, and timeout management. Built-in TypeScript support.

**Alternatives considered:**
- Fetch API: Would require manual interceptor wrapper
- React Query: Overcomplicates data fetching for this scope

**Decision:** Axios with custom interceptor wrapper.

### 5. Feature-Sliced Design (FSD) Architecture
**Why:** FSD provides clear separation of concerns, scalability for team growth, and prevents spaghetti imports. Each feature is self-contained.

**Structure:**
```
frontend/
├── src/
│   ├── shared/          # Reusable UI atoms, hooks, utilities
│   │   ├── ui/          # Button, Card, Modal, Form
│   │   ├── hooks/       # useAPI, useLocalStorage, etc.
│   │   ├── utils/       # helpers, formatters
│   │   └── constants/   # app constants
│   ├── entities/        # Data models (User, Product, Order)
│   ├── features/        # Feature-specific logic
│   │   ├── auth/        # Auth store, login form (CHANGE-01)
│   │   ├── cart/        # Cart store, cart widget (CHANGE-08)
│   │   └── ...
│   ├── pages/           # Page components (CHANGE-02)
│   ├── app/             # App wrapper, providers, layout
│   └── config/          # App configuration, constants
├── public/
├── .env.example
├── vite.config.ts
├── tsconfig.json
└── package.json
```

**Alternatives considered:**
- Flat structure: Doesn't scale beyond 5-10 developers
- Atomic design (atoms/molecules): Less suitable for feature organization

**Decision:** FSD is adopted.

### 6. Store Factory Pattern for Zustand
**Why:** Instead of creating stores ad-hoc, a factory function ensures consistency: typing, devtools, persistence hooks. Reduces boilerplate and keeps stores predictable.

**Pattern:**
```typescript
// createStore.ts
export const createStore = <T,>(initialState: T) => {
  return create<Store<T>>((set, get) => ({
    ...initialState,
    // common actions
  }));
};

// authStore.ts
export const useAuthStore = createStore<AuthState>({
  user: null,
  token: null,
});
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Zustand lacks time-travel debugging (Redux DevTools) | Use devtools plugin if needed; logging sufficient for this scope |
| Tailwind CSS bundle bloat if not tree-shaken | PurgeCSS configured in Vite to remove unused classes |
| FSD structure may feel over-engineered initially | Provides ROI as project grows; non-negotiable for 16 changes |
| TypeScript strict mode causes friction early | Worth the quality payoff; errors caught at compile time |
| No SSR capability with Vite + Zustand | Not needed for Food Store (SPA architecture) |

## Migration Plan

1. Initialize Vite project: `npm create vite@latest frontend -- --template react-ts`
2. Install dependencies: Zustand, Axios, Tailwind, ESLint, Prettier
3. Create FSD folder structure
4. Implement base store factory and example stores (auth, ui)
5. Create HTTP client with Axios + interceptors
6. Add Tailwind config with theme variables
7. Create base UI components (Button, Card, Modal, Form)
8. Set up Husky + lint-staged for pre-commit hooks
9. Commit scaffolded project: "feat: frontend setup with Zustand and Tailwind"

No rollback needed; this is green-field scaffolding.

## Open Questions

- Should we use `pnpm` instead of `npm`? (Faster, monorepo-friendly) → Recommend pnpm if team agrees
- Vitest for unit tests in frontend, or Jest? (Vitest integrates better with Vite) → Defer to CHANGE-16
- Should dark mode be user preference stored in Zustand or browser preference? → Implement both, default to browser preference
