# Food Store - Frontend

Modern React 19 frontend for Food Store built with TypeScript, Zustand, and Tailwind CSS.

## Quick Start

### Prerequisites
- Node.js 18+
- npm or pnpm

### Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start dev server**
   ```bash
   npm run dev
   ```
   
   Open [http://localhost:5173](http://localhost:5173) in your browser.

## Available Scripts

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Project Structure

This project follows **Feature-Sliced Design (FSD)** principles:

```
src/
├── app/              # App root component and providers
├── pages/            # Page components (Login, Home, etc.)
├── features/         # Feature modules
│   ├── auth/        # Authentication
│   ├── ui/          # UI state (theme, toasts)
│   └── cart/        # Shopping cart
├── entities/         # Data models and types
├── shared/           # Reusable utilities and components
│   ├── ui/          # UI components (Button, Card, etc.)
│   ├── hooks/       # Custom hooks
│   ├── utils/       # Utility functions
│   ├── http/        # HTTP client and interceptors
│   ├── store/       # Store factory
│   └── constants/   # App constants
└── config/          # App configuration
```

### FSD Benefits
- **Scalability**: Easy to add new features without affecting existing code
- **Testability**: Features are isolated and independently testable
- **Maintainability**: Clear separation of concerns
- **Collaboration**: Team members can work on different features in parallel

## Key Technologies

### Core
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Lightning-fast build tool

### State Management
- **Zustand** - Lightweight global state management

### Styling
- **Tailwind CSS** - Utility-first CSS framework
- **Dark mode support** - Built-in with class-based approach

### API Integration
- **Axios** - HTTP client with interceptors

### Development
- **ESLint** - Code quality
- **Prettier** - Code formatting

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_DEBUG=true
VITE_APP_NAME=Food Store
```

### TypeScript Path Aliases

Configured in `tsconfig.json`:
- `@/*` → `src/*`
- `@shared/*` → `src/shared/*`
- `@features/*` → `src/features/*`
- `@entities/*` → `src/entities/*`
- `@pages/*` → `src/pages/*`

## Store Management (Zustand)

### Auth Store
```typescript
import { useAuthStore } from '@/features/auth/store'

const { user, token, logout } = useAuthStore()
```

### UI Store
```typescript
import { useUIStore } from '@/features/ui/store'

const { theme, toggleTheme, showToast } = useUIStore()
```

## API Integration

The HTTP client is pre-configured with:
- Base URL from environment variables
- Request interceptor to add JWT tokens
- Response interceptor to handle 401 errors
- Request/response logging in debug mode

```typescript
import { apiClient } from '@/shared/http'

// Usage
const response = await apiClient.get('/productos')
```

## Components

Pre-built UI components available in `@/shared/ui`:

- **Button** - Primary, secondary, danger variants
- **Card** - Container with optional hover effects
- **Input** - Form input with validation
- **Modal** - Dialog with actions
- **Select** - Dropdown
- **Textarea** - Multi-line input
- **Toast** - Notifications
- **Skeleton** - Loading placeholders

## Custom Hooks

- **useAuth()** - Access auth state and methods
- **useTheme()** - Access and toggle theme
- **useLocalStorage()** - Persist state to localStorage

## Utilities

Located in `@/shared/utils`:

### Formatters
- `formatPrice(number)` - Currency formatting
- `formatDate(Date | string)` - Date formatting
- `formatDateTime(Date | string)` - DateTime formatting
- `truncateText(string, length)` - Text truncation
- `capitalize(string)` - Capitalize text

### Validators
- `isValidEmail(string)` - Email validation
- `isValidPhone(string)` - Phone validation
- `isValidUrl(string)` - URL validation
- `isStrongPassword(string)` - Password strength

### Storage
- `getFromStorage(key, default)` - Get from localStorage
- `setToStorage(key, value)` - Save to localStorage
- `removeFromStorage(key)` - Remove from localStorage
- `clearStorage()` - Clear all app data

## Building for Production

```bash
npm run build
```

Output is in the `dist/` directory. All code is minified and optimized.

## Troubleshooting

### Port 5173 already in use
```bash
npm run dev -- --port 3000
```

### TypeScript errors
Ensure `strict: true` in `tsconfig.json` and install types:
```bash
npm install -D @types/react @types/react-dom
```

### Tailwind styles not applying
- Check `tailwind.config.ts` content paths
- Ensure `index.css` is imported in `main.tsx`

## Contributing

1. Follow FSD structure
2. Use TypeScript strict mode
3. Run `npm run lint` before committing
4. Add components to barrel exports (`index.ts`)

## Next Steps

This is CHANGE-00b (Frontend Setup). Next changes:
- CHANGE-00c: Backend CORS + Rate Limiting
- CHANGE-00d: Seed Data + Base Tests
- CHANGE-01: Authentication (Login/Register)
- ...and more!

## License

MIT
