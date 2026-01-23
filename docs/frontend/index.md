# Frontend Documentation

## Overview

The ELIMS frontend is a modern React application built with TypeScript, providing a rich user interface for laboratory instrument management. It features real-time data updates, responsive design, and comprehensive data visualization.

## Technology Stack

- **Framework**: [React](https://react.dev/) 19.1+
- **Language**: TypeScript 5+
- **Build Tool**: [Vite](https://vite.dev/) 6+
- **Package Manager**: [Bun](https://bun.sh/)
- **Routing**: [TanStack Router](https://tanstack.com/router) 1.142+
- **State Management**: [TanStack Query](https://tanstack.com/query) 5.90+
- **UI Components**: [Radix UI](https://www.radix-ui.com/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) 4+
- **Forms**: [React Hook Form](https://react-hook-form.com/) + [Zod](https://zod.dev/)
- **Icons**: [Lucide React](https://lucide.dev/) + [React Icons](https://react-icons.github.io/react-icons/)
- **HTTP Client**: Axios 1.13+
- **Testing**: [Playwright](https://playwright.dev/) 1.57+
- **Linting**: [Biome](https://biomejs.dev/) 2.3+

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Application entry point
│   ├── index.css             # Global styles
│   ├── vite-env.d.ts         # Vite type definitions
│   ├── utils.ts              # Utility functions
│   ├── routeTree.gen.ts      # Auto-generated router config
│   ├── client/               # API client (auto-generated)
│   │   ├── index.ts
│   │   ├── sdk.gen.ts
│   │   ├── types.gen.ts
│   │   └── core/
│   ├── components/           # React components
│   │   ├── theme-provider.tsx
│   │   ├── Common/           # Common components
│   │   └── ui/               # UI components (shadcn)
│   ├── hooks/                # Custom React hooks
│   │   └── useMobile.ts
│   ├── lib/                  # Libraries and utilities
│   │   └── utils.ts
│   └── routes/               # Route components
│       ├── __root.tsx        # Root layout
│       ├── _layout.tsx       # App layout
│       └── _layout/          # Nested routes
├── public/                   # Static assets
│   └── assets/
│       └── images/
├── tests/                    # E2E tests
│   ├── config.ts
│   ├── home.spec.ts
│   └── utils/
├── components.json           # shadcn/ui config
├── Dockerfile                # Production Docker image
├── Dockerfile.playwright     # Playwright test image
├── nginx.conf                # Nginx configuration
├── openapi-ts.config.ts      # API client generation config
├── playwright.config.ts      # Playwright configuration
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript config
├── tsconfig.build.json       # Build TypeScript config
├── tsconfig.node.json        # Node TypeScript config
├── vite.config.ts            # Vite configuration
└── biome.json               # Biome linting config
```

## Architecture

### Component Hierarchy

```
App (main.tsx)
  ├── Router
  │   ├── Root Layout (__root.tsx)
  │   │   ├── Theme Provider
  │   │   ├── Query Client Provider
  │   │   └── Error Boundary
  │   └── Routes
  │       ├── Layout (_layout.tsx)
  │       │   ├── Header
  │       │   ├── Sidebar
  │       │   └── Main Content
  │       └── Pages
  │           ├── Dashboard
  │           ├── Instruments
  │           ├── Locations
  │           └── Settings
```

### Data Flow

```
User Interaction
      ↓
React Component
      ↓
TanStack Query Hook
      ↓
API Client (Axios)
      ↓
Backend API
      ↓
Response Processing
      ↓
State Update (TanStack Query Cache)
      ↓
React Re-render
```

## Key Features

### 1. Routing (TanStack Router)

File-based routing with type-safe navigation:

```typescript
// routes/__root.tsx
import { createRootRoute, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'

export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />
      {import.meta.env.DEV && <TanStackRouterDevtools />}
    </>
  ),
})
```

```typescript
// routes/_layout/index.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_layout/')({
  component: Dashboard,
})

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      {/* Dashboard content */}
    </div>
  )
}
```

### 2. Data Fetching (TanStack Query)

Declarative data fetching with caching:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { InstrumentsService } from '@/client'

// Fetch instruments
function useInstruments() {
  return useQuery({
    queryKey: ['instruments'],
    queryFn: () => InstrumentsService.listInstruments(),
  })
}

// Create instrument
function useCreateInstrument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: InstrumentsService.createInstrument,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['instruments'] })
    },
  })
}

// Usage in component
function InstrumentsList() {
  const { data, isLoading, error } = useInstruments()
  const createMutation = useCreateInstrument()

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      {data?.map(instrument => (
        <div key={instrument.id}>{instrument.name}</div>
      ))}
      <button onClick={() => createMutation.mutate({ name: 'New' })}>
        Add Instrument
      </button>
    </div>
  )
}
```

### 3. Forms (React Hook Form + Zod)

Type-safe form validation:

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

// Schema
const instrumentSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  model: z.string().min(1, 'Model is required'),
  serial_number: z.string().min(1, 'Serial number is required'),
  location_id: z.number().positive(),
})

type InstrumentForm = z.infer<typeof instrumentSchema>

// Component
function InstrumentForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<InstrumentForm>({
    resolver: zodResolver(instrumentSchema),
  })

  const onSubmit = (data: InstrumentForm) => {
    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      {errors.name && <span>{errors.name.message}</span>}

      <input {...register('model')} />
      {errors.model && <span>{errors.model.message}</span>}

      <button type="submit">Submit</button>
    </form>
  )
}
```

### 4. UI Components (Radix UI + Tailwind)

Accessible, styled components:

```typescript
// components/ui/button.tsx
import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)

export { Button, buttonVariants }
```

### 5. Theme Support

Dark/Light mode with next-themes:

```typescript
// components/theme-provider.tsx
import { ThemeProvider as NextThemesProvider } from 'next-themes'

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  )
}

// Usage in component
import { useTheme } from 'next-themes'

function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      Toggle Theme
    </button>
  )
}
```

## API Client Generation

### Configuration

```typescript
// openapi-ts.config.ts
import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
  client: '@hey-api/client-axios',
  input: './openapi.json',
  output: {
    path: './src/client',
    format: 'prettier',
    lint: 'biome',
  },
  types: {
    enums: 'javascript',
  },
})
```

### Generate Client

```bash
# Download OpenAPI spec from backend
curl http://localhost:8000/openapi.json > openapi.json

# Generate TypeScript client
bun run generate-client
```

### Using Generated Client

```typescript
import { InstrumentsService } from '@/client'

// Configure base URL
import { OpenAPI } from '@/client/core/OpenAPI'
OpenAPI.BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Use service methods
const instruments = await InstrumentsService.listInstruments()
const instrument = await InstrumentsService.getInstrument({ id: 1 })
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/FabienMeyer/elims.git
cd elims/frontend

# Install dependencies
bun install

# Copy environment file
cp ../.env.example ../.env
# Edit .env with your configuration

# Generate API client
bun run generate-client

# Start development server
bun run dev
```

### Available Scripts

```bash
# Development server (with HMR)
bun run dev

# Build for production
bun run build

# Preview production build
bun run preview

# Lint and auto-fix
bun run lint

# Generate API client
bun run generate-client

# Run E2E tests
bun run test

# Run tests with UI
bun run test:ui
```

### Development Server

Access the application at: http://localhost:5173

Features:

- **Hot Module Replacement (HMR)**: Instant updates
- **React DevTools**: Browser extension
- **TanStack Query DevTools**: Embedded in app
- **TanStack Router DevTools**: Embedded in app

## Testing

### Playwright E2E Tests

#### Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'bun run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

#### Example Test

```typescript
// tests/home.spec.ts
import { test, expect } from '@playwright/test'

test('homepage loads correctly', async ({ page }) => {
  await page.goto('/')

  // Check title
  await expect(page).toHaveTitle(/ELIMS/)

  // Check heading
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
})

test('can navigate to instruments page', async ({ page }) => {
  await page.goto('/')

  // Click instruments link
  await page.getByRole('link', { name: 'Instruments' }).click()

  // Check URL
  await expect(page).toHaveURL(/\/instruments/)

  // Check heading
  await expect(page.getByRole('heading', { name: 'Instruments' })).toBeVisible()
})
```

#### Running Tests

```bash
# Run all tests
bun run test

# Run with UI mode
bun run test:ui

# Run specific test file
bunx playwright test tests/home.spec.ts

# Run in headed mode (see browser)
bunx playwright test --headed

# Debug mode
bunx playwright test --debug

# Generate test
bunx playwright codegen http://localhost:5173
```

## Build & Deployment

### Production Build

```bash
# Build
bun run build

# Preview build
bun run preview
```

Output directory: `dist/`

### Docker Deployment

#### Multi-stage Dockerfile

```dockerfile
# Build stage
FROM oven/bun:1 AS builder

WORKDIR /app

COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
}
```

### Environment Variables

```bash
# .env
VITE_API_URL=http://localhost:8000
```

Access in code:

```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

## Styling

### Tailwind CSS

Global styles in `index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    /* ... */
  }

  .dark {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 0 0% 9%;
    /* ... */
  }
}
```

### Utility Functions

```typescript
// lib/utils.ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

Usage:

```typescript
<div className={cn('base-class', condition && 'conditional-class')} />
```

## Best Practices

### Component Organization

```typescript
// 1. Imports
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

// 2. Types
interface ComponentProps {
  title: string
  onAction?: () => void
}

// 3. Component
export function Component({ title, onAction }: ComponentProps) {
  // 4. Hooks
  const [state, setState] = useState(false)
  const { data } = useQuery(...)

  // 5. Handlers
  const handleClick = () => {
    setState(true)
    onAction?.()
  }

  // 6. Render
  return (
    <div onClick={handleClick}>
      {title}
    </div>
  )
}
```

### Performance

1. **Code Splitting**: Use dynamic imports

   ```typescript
   const Component = lazy(() => import('./Component'))
   ```

1. **Memoization**: Use `useMemo` and `useCallback`

   ```typescript
   const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b])
   const memoizedCallback = useCallback(() => doSomething(a, b), [a, b])
   ```

1. **Virtual Lists**: For long lists

   ```typescript
   import { useVirtualizer } from '@tanstack/react-virtual'
   ```

### Accessibility

1. **Semantic HTML**: Use proper elements
1. **ARIA Labels**: Add labels for screen readers
1. **Keyboard Navigation**: Support keyboard interactions
1. **Focus Management**: Manage focus states
1. **Color Contrast**: Ensure sufficient contrast

### Security

1. **XSS Prevention**: React escapes by default
1. **Content Security Policy**: Configure headers
1. **Sanitize User Input**: For dangerouslySetInnerHTML
1. **HTTPS Only**: In production
1. **Secure Cookies**: For authentication

## Troubleshooting

### Common Issues

1. **API Connection Errors**

   - Check VITE_API_URL
   - Verify backend is running
   - Check CORS configuration

1. **Build Errors**

   - Clear node_modules and reinstall
   - Check TypeScript errors
   - Verify import paths

1. **Hot Reload Not Working**

   - Restart development server
   - Check file watcher limits
   - Clear Vite cache

### Debugging

```typescript
// React DevTools
// Browser extension for inspecting components

// TanStack Query DevTools
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// TanStack Router DevTools
import { TanStackRouterDevtools } from '@tanstack/router-devtools'

// Console logging
console.log('Debug:', data)
console.table(array)
console.error('Error:', error)
```

## Related Documentation

- [Backend Documentation](../backend/index.md)
- [Workflows Documentation](../workflows/index.md)
- [Testing Documentation](../workflows/test-frontend.md)
