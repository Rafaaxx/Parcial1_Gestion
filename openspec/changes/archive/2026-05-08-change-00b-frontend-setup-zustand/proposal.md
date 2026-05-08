## Why

CHANGE-00a established the backend infrastructure (FastAPI, SQLModel, UoW pattern). Now we need to build the frontend foundation with React + Zustand state management. This enables all subsequent frontend changes: authentication UI, navigation, shopping cart, orders, and admin dashboard. Without this, we cannot implement any user-facing features.

## What Changes

- Initialize React 19 project with TypeScript, Vite bundler, and modern tooling
- Set up Zustand for global state management with proper TypeScript types
- Create base store abstractions (`createAuthStore`, `createUIStore`, `createCartStore` signatures) for consistency across all future stores
- Configure Axios HTTP client with interceptors for API calls
- Set up project structure following Feature-Sliced Design (FSD) convention
- Add base styling system (Tailwind CSS or styled-components) with theme support for dark/light mode
- Create wrapper components for common patterns (containers, form layouts, modal dialogs, alerts)
- Add mock API responses for development (optional MSW - Mock Service Worker setup)

## Capabilities

### New Capabilities
- `zustand-stores`: Global state management system with typed, reusable store creators and selectors for auth, UI, cart, and other domains
- `http-client`: Async HTTP client with Axios, request/response interceptors, error handling, and retry logic
- `ui-system`: Component library and design system with Tailwind CSS, theme support, and reusable atoms/molecules
- `project-structure`: Feature-Sliced Design folder structure for scalable frontend organization

### Modified Capabilities
<!-- No existing capabilities are being modified at spec level -->

## Impact

- Frontend codebase: `frontend/` directory fully scaffolded
- Dependencies added: React 19, TypeScript 5.x, Zustand, Axios, Tailwind CSS, Vite
- Project structure impacts: All future frontend work follows FSD pattern
- Build pipeline: Vite replaces Create React App (faster, modern)
- Development experience: HMR (Hot Module Replacement), type safety, integrated linting
