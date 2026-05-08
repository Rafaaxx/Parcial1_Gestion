## 1. Project Setup

- [ ] 1.1 Create React 19 project with Vite: `npm create vite@latest frontend -- --template react-ts`
- [ ] 1.2 Navigate to frontend directory and install dependencies: `cd frontend && npm install`
- [ ] 1.3 Verify Vite dev server runs: `npm run dev` (should start on http://localhost:5173)

## 2. Install Dependencies

- [ ] 2.1 Install Zustand: `npm install zustand`
- [ ] 2.2 Install Axios: `npm install axios`
- [ ] 2.3 Install Tailwind CSS: `npm install -D tailwindcss postcss autoprefixer`
- [ ] 2.4 Initialize Tailwind: `npx tailwindcss init -p`
- [ ] 2.5 Install ESLint and Prettier: `npm install -D eslint prettier eslint-config-prettier`
- [ ] 2.6 Install TypeScript and types: `npm install -D typescript @types/react @types/react-dom`
- [ ] 2.7 Install Zustand devtools (optional): `npm install zustand-devtools`

## 3. TypeScript Configuration

- [ ] 3.1 Configure tsconfig.json with strict mode and path aliases: `@/*` → `src/*`, `@shared` → `src/shared`, `@features` → `src/features`
- [ ] 3.2 Enable `strict: true` and `skipLibCheck: true`
- [ ] 3.3 Test path aliases by importing from `@/shared/ui`

## 4. Vite Configuration

- [ ] 4.1 Update vite.config.ts with path alias plugin: `resolve.alias` for `@` → `src`
- [ ] 4.2 Configure Vite to use HMR on save
- [ ] 4.3 Test HMR: save a file and verify browser auto-refreshes

## 5. Feature-Sliced Design (FSD) Structure

- [ ] 5.1 Create src directory structure:
  ```
  src/
  ├── app/
  ├── pages/
  ├── features/
  ├── entities/
  └── shared/
      ├── ui/
      ├── hooks/
      ├── utils/
      ├── constants/
      └── types/
  ```
- [ ] 5.2 Create placeholder index.ts files in each directory for barrel exports
- [ ] 5.3 Document FSD structure in a shared README (e.g., `src/FSD_STRUCTURE.md`)

## 6. Tailwind CSS Setup

- [ ] 6.1 Update tailwind.config.ts with theme customization (colors, spacing, breakpoints)
- [ ] 6.2 Create tailwind.css in src/ with Tailwind directives: `@tailwind base; @tailwind components; @tailwind utilities;`
- [ ] 6.3 Import tailwind.css in src/main.tsx
- [ ] 6.4 Configure dark mode support: `darkMode: 'class'` in tailwind.config.ts
- [ ] 6.5 Test Tailwind: create a simple styled div and verify styles apply

## 7. Zustand Store Factory and Base Stores

- [ ] 7.1 Create `src/shared/store/createStore.ts` - factory function with TypeScript generics
- [ ] 7.2 Create `src/features/auth/store.ts` - auth store with `{ user, token, refreshToken, setUser(), logout() }`
- [ ] 7.3 Create `src/features/ui/store.ts` - UI store with `{ theme, toast, toggleTheme(), showToast() }`
- [ ] 7.4 Create `src/features/cart/types.ts` - CartState interface (not fully implemented, for CHANGE-08)
- [ ] 7.5 Test stores in browser console: `useAuthStore.setState({ user: {...} })`
- [ ] 7.6 Add localStorage persistence to UI store (theme preference)

## 8. HTTP Client (Axios)

- [ ] 8.1 Create `src/shared/http/client.ts` - Axios instance with baseURL and timeout configuration
- [ ] 8.2 Create `src/shared/http/interceptors.ts` - request interceptor that adds Bearer token from auth store
- [ ] 8.3 Add response interceptor for error handling: 401 → refresh token → retry
- [ ] 8.4 Add response interceptor for 401 → redirect to login (defer full nav to CHANGE-02)
- [ ] 8.5 Create `src/shared/http/index.ts` - export client instance
- [ ] 8.6 Test HTTP client: make a GET request and verify token is included in headers

## 9. Base UI Components (shared/ui)

- [ ] 9.1 Create Button component: `src/shared/ui/Button.tsx` with variants (primary, secondary, danger) and states (loading, disabled)
- [ ] 9.2 Create Card component: `src/shared/ui/Card.tsx` with padding, border, shadow, and optional hover effect
- [ ] 9.3 Create Modal component: `src/shared/ui/Modal.tsx` with overlay, backdrop click handling, and action buttons
- [ ] 9.4 Create Input component: `src/shared/ui/Input.tsx` with label, placeholder, validation states, and error message
- [ ] 9.5 Create Textarea component: `src/shared/ui/Textarea.tsx` - similar to Input
- [ ] 9.6 Create Select component: `src/shared/ui/Select.tsx` - dropdown with typed options
- [ ] 9.7 Create Toast/Alert component: `src/shared/ui/Toast.tsx` - dismissible notification
- [ ] 9.8 Create Skeleton/Loader component: `src/shared/ui/Skeleton.tsx` - shimmer placeholder

## 10. Shared Hooks (shared/hooks)

- [ ] 10.1 Create `useLocalStorage.ts` - hook for persisting state to localStorage
- [ ] 10.2 Create `useTheme.ts` - hook for accessing and toggling theme from UI store
- [ ] 10.3 Create `useAuth.ts` - hook for accessing auth store (user, token)
- [ ] 10.4 Test hooks: use them in a test component and verify functionality

## 11. Shared Utilities (shared/utils)

- [ ] 11.1 Create `formatters.ts` - utility functions: `formatPrice()`, `formatDate()`, `truncateText()`
- [ ] 11.2 Create `validators.ts` - validation helpers: `isValidEmail()`, `isValidPhone()`
- [ ] 11.3 Create `storage.ts` - localStorage wrapper for type-safe access
- [ ] 11.4 Test utilities: create unit tests or manual verification

## 12. Configuration Files

- [ ] 12.1 Create `.env.example` with required variables: `VITE_API_BASE_URL`, `VITE_DEBUG`, `VITE_APP_NAME`
- [ ] 12.2 Create `.env` (local) from `.env.example` and update with dev values
- [ ] 12.3 Create `src/config/env.ts` - typed environment variable loader
- [ ] 12.4 Update package.json with scripts: `dev`, `build`, `preview`, `lint`

## 13. Linting and Code Quality

- [ ] 13.1 Create `.eslintrc.cjs` with React + TypeScript rules
- [ ] 13.2 Create `.prettierrc` with code formatting rules (printWidth: 100, semi: true, etc.)
- [ ] 13.3 Install Husky for pre-commit hooks: `npm install husky --save-dev`
- [ ] 13.4 Create `.husky/pre-commit` - run linter and formatter before commits
- [ ] 13.5 Test linting: make a file with bad formatting and verify lint catches it

## 14. Entry Point and App Wrapper

- [ ] 14.1 Update `src/main.tsx` - import Tailwind CSS, mount App component
- [ ] 14.2 Create `src/app/App.tsx` - root component with providers and theme context
- [ ] 14.3 Wrap app with theme provider that applies `dark:` class based on UI store
- [ ] 14.4 Test app: `npm run dev` should render without errors

## 15. Documentation

- [ ] 15.1 Create `frontend/README.md` - setup instructions, available scripts, folder structure
- [ ] 15.2 Create `frontend/ARCHITECTURE.md` - FSD principles, store patterns, component guidelines
- [ ] 15.3 Add inline JSDoc comments to store factory and HTTP client
- [ ] 15.4 Document environment variables in `frontend/.env.example`

## 16. Verification and Testing

- [ ] 16.1 Verify dev server starts: `npm run dev` (no errors)
- [ ] 16.2 Verify Tailwind styles apply: see styled components in browser
- [ ] 16.3 Verify TypeScript compilation: `npm run build` succeeds
- [ ] 16.4 Verify path aliases work: import from `@/shared/ui`
- [ ] 16.5 Verify Zustand stores work: open browser console and test `useAuthStore`
- [ ] 16.6 Verify HTTP client works: test with `curl http://localhost:8000/health` and verify frontend can call it
- [ ] 16.7 Verify linting passes: `npm run lint` with no errors
- [ ] 16.8 Verify dark mode toggle: click theme toggle and see CSS classes change

## 17. Git Commit

- [ ] 17.1 Stage all changes: `git add .`
- [ ] 17.2 Create commit: `git commit -m "feat: frontend setup with Zustand, Tailwind, and FSD structure"`
- [ ] 17.3 Verify commit: `git log --oneline | head -5`
