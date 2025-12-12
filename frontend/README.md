# Aurigo Frontend

Modern, responsive Next.js 14 frontend for the Aurigo EB-1A Attorney Letter Generation System with dark/light theme support.

## Features

- **Modern UI/UX**: Clean, professional interface built with Next.js 14 and Tailwind CSS
- **Dark/Light Theme**: Seamless theme switching with persistent preferences
- **Real-time Updates**: Live progress tracking for case processing
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Type-Safe**: Built with TypeScript for robust code quality
- **API Integration**: Complete integration with backend REST API
- **Authentication**: JWT-based secure authentication with protected routes

## Pages

### Authentication
- **Login** (`/login`): User sign-in with validation
- **Register** (`/register`): New user registration

### Dashboard
- **Dashboard** (`/dashboard`): Overview with case statistics and recent activity
- **Case List** (`/cases`): View all cases with filtering and status indicators
- **Case Upload** (`/cases/upload`): Upload case folders with drag-and-drop support
- **Case Detail** (`/cases/[id]`): Real-time processing status with progress tracking
- **Letter Preview** (`/cases/[id]/preview`): View generated attorney letter with exhibit index

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS with dark mode support
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Forms**: React Hook Form + Zod validation
- **Icons**: Lucide React

## Setup

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000` (or set `NEXT_PUBLIC_API_URL`)

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Update .env.local with your backend URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Visit `http://localhost:3000`

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js 14 App Router
│   │   ├── (auth)/              # Authentication routes
│   │   │   ├── login/           # Login page
│   │   │   └── register/        # Registration page
│   │   ├── (main)/              # Protected routes
│   │   │   ├── dashboard/       # Dashboard page
│   │   │   └── cases/           # Case management
│   │   │       ├── page.tsx     # Case list
│   │   │       ├── upload/      # Upload page
│   │   │       └── [id]/        # Dynamic case routes
│   │   │           ├── page.tsx           # Case detail
│   │   │           └── preview/page.tsx  # Letter preview
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Home page (redirects)
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── ui/                  # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   └── input.tsx
│   │   ├── providers.tsx        # Context providers
│   │   └── theme-toggle.tsx     # Theme switcher
│   └── lib/
│       ├── api/                 # API client layer
│       │   └── cases.ts         # Case API functions
│       ├── store/               # State management
│       │   ├── auth.ts          # Auth store
│       │   └── theme.ts         # Theme store
│       ├── api.ts               # Axios instance
│       └── utils.ts             # Utility functions
├── public/                      # Static assets
├── tailwind.config.ts           # Tailwind configuration
├── tsconfig.json               # TypeScript config
└── package.json                # Dependencies
```

## Key Features

### Theme System

The app supports light and dark modes with persistent preferences:

```tsx
import { useThemeStore } from '@/lib/store/theme'

function MyComponent() {
  const { theme, toggleTheme } = useThemeStore()

  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}
    </button>
  )
}
```

### Authentication

Protected routes automatically redirect unauthenticated users:

```tsx
import { useAuthStore } from '@/lib/store/auth'

function ProtectedPage() {
  const { user, logout } = useAuthStore()
  // User is guaranteed to be authenticated
}
```

### API Integration

Type-safe API calls with error handling:

```tsx
import { casesApi } from '@/lib/api/cases'

async function uploadCase(name: string, file: File) {
  try {
    const response = await casesApi.uploadCase(name, file)
    console.log('Uploaded case:', response.case_id)
  } catch (error) {
    console.error('Upload failed:', error)
  }
}
```

### Real-time Progress Tracking

Case detail page polls for updates every 3 seconds during processing:

```tsx
// Automatically updates progress bar and status
useEffect(() => {
  const interval = setInterval(() => {
    if (caseData?.status === 'processing') {
      loadCaseStatus() // Fetch latest status
    }
  }, 3000)
  return () => clearInterval(interval)
}, [caseData?.status])
```

## Styling

### Tailwind Dark Mode

Use `dark:` prefix for dark mode styles:

```tsx
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Content adapts to theme
</div>
```

### Color Palette

- **Primary**: Blue (`primary-600`)
- **Success**: Green
- **Warning**: Yellow
- **Error**: Red
- **Neutral**: Gray scale

## API Endpoints Used

The frontend integrates with these backend endpoints:

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `GET /api/auth/me` - Get current user

### Cases
- `GET /api/cases` - List all cases
- `POST /api/cases/upload` - Upload case folder
- `POST /api/cases/{id}/process` - Start processing
- `GET /api/cases/{id}/status` - Get processing status
- `GET /api/cases/{id}/preview` - Preview letter
- `GET /api/cases/{id}/download` - Get download links
- `DELETE /api/cases/{id}` - Delete case

## Development

### Adding a New Page

1. Create page file in `src/app/` directory
2. Use TypeScript for type safety
3. Add dark mode styles with `dark:` prefix
4. Connect to API via `src/lib/api/`

Example:

```tsx
// src/app/(main)/my-page/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { casesApi } from '@/lib/api/cases'

export default function MyPage() {
  const [data, setData] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    const result = await casesApi.listCases()
    setData(result)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Content */}
    </div>
  )
}
```

### Adding New API Endpoints

1. Add types to `src/lib/api/cases.ts`
2. Add API function
3. Use in components

```tsx
// src/lib/api/cases.ts
export const casesApi = {
  myNewEndpoint: async () => {
    const response = await api.get('/my-endpoint')
    return response.data
  }
}
```

## Environment Variables

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Responsive Breakpoints

- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

Use Tailwind's responsive prefixes:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* 1 column on mobile, 2 on tablet, 3 on desktop */}
</div>
```

## Troubleshooting

### "Cannot connect to backend"
- Ensure backend is running on `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is enabled in backend

### "Theme not persisting"
- Check browser local storage
- Ensure `ThemeProvider` is wrapping app in `layout.tsx`

### "Authentication not working"
- Clear browser local storage
- Check token in `localStorage.getItem('token')`
- Verify JWT token is valid

## Contributing

1. Follow TypeScript best practices
2. Add dark mode support to all new components
3. Ensure responsive design on all screen sizes
4. Test with backend API before committing
5. Use semantic commit messages

## License

MIT License - See parent project LICENSE file
