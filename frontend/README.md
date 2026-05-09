# Frontend

## Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── assets/          # Static assets
│   ├── components/      # Vue components
│   │   ├── common/      # Common components
│   │   ├── layout/      # Layout components
│   │   ├── article/     # Article-related components
│   │   └── admin/       # Admin components
│   ├── views/           # Page views
│   │   ├── blog/        # Blog pages
│   │   └── admin/       # Admin pages
│   ├── router/          # Vue Router configuration
│   ├── stores/          # Pinia stores
│   ├── utils/           # Utility functions
│   ├── api/             # API client and endpoints
│   ├── composables/     # Vue composables
│   └── types/           # TypeScript types
├── public/              # Public assets
├── package.json
├── vite.config.js
├── tailwind.config.js
└── tsconfig.json
```

## Technology Stack

- **Vue 3** - Frontend framework
- **Vite** - Build tool
- **TypeScript** - Type safety
- **Pinia** - State management
- **Vue Router** - Routing
- **Naive UI** - UI component library
- **Axios** - HTTP client
- **TailwindCSS** - Utility-first CSS
- **VueUse** - Composition utilities

## Environment Variables

- `VITE_API_BASE_URL` - Backend API base URL (default: `/api/v1`)

## Development Guidelines

### Component Structure

```vue
<template>
  <!-- Template code -->
</template>

<script setup lang="ts">
// Script code
</script>

<style scoped>
/* Styles */
</style>
```

### API Usage

```typescript
import { articleApi } from '@/api'

// Get articles
const articles = await articleApi.getList({ page: 1, limit: 10 })

// Get article detail
const article = await articleApi.getDetail('my-article-slug')
```

### State Management

```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const { user, isAuthenticated } = authStore
```
