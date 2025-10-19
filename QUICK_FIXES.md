# Quick Fixes for Monorepo Structure

## 🚨 Critical Issues to Fix Immediately

### 1. Remove Duplicate Workspace Configuration

**Problem**: Both `package.json` and `pnpm-workspace.yaml` define workspaces
**Fix**: Remove workspace definition from root `package.json`

```json
// package.json - REMOVE this section:
{
  "workspaces": [
    "apps/web",
    "packages/js/*"
  ]
}
```

**Keep only**: `pnpm-workspace.yaml`

### 2. Fix Port Configuration Inconsistency

**Problem**: API runs on port 8002, but frontend expects port 8000
**Fix**: Update frontend environment configuration

```bash
# apps/web/.env.local
NEXT_PUBLIC_API_BASE=http://localhost:8002  # Match actual API port
```

### 3. Implement Shared JS Package Structure

**Problem**: `packages/js/ui-kit` is empty but referenced in workspace
**Fix**: Create proper shared package structure

```bash
# Create packages/js/ui-kit/package.json
{
  "name": "@med-rag/ui-kit",
  "version": "0.1.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "dependencies": {
    "react": "^18.2.0",
    "@radix-ui/react-*": "*"
  }
}
```

### 4. Standardize Build Scripts

**Problem**: Inconsistent script naming and execution
**Fix**: Update root package.json scripts

```json
{
  "scripts": {
    "dev": "concurrently \"just dev-api\" \"just dev-web\"",
    "build": "pnpm --filter web build && uv run --project apps/api python -m build",
    "test": "uv run pytest && pnpm --filter web test",
    "lint": "uv run ruff check . && pnpm --filter web lint",
    "typecheck": "uv run mypy . && pnpm --filter web typecheck"
  }
}
```

## 🔧 Configuration Improvements

### 1. Create Shared ESLint Configuration

```bash
# packages/js/eslint-config/package.json
{
  "name": "@med-rag/eslint-config",
  "version": "0.1.0",
  "main": "index.js",
  "dependencies": {
    "eslint-config-next": "14.1.0",
    "eslint-config-prettier": "^9.1.0"
  }
}
```

### 2. Add Missing Dependencies

```bash
# Root package.json - Add missing dev dependencies
{
  "devDependencies": {
    "concurrently": "^8.2.2",
    "cross-env": "^7.0.3"
  }
}
```

### 3. Fix TypeScript Configuration

```json
// apps/web/tsconfig.json - Add path mapping
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@med-rag/ui-kit": ["../../packages/js/ui-kit/src"]
    }
  }
}
```

## 🧪 Testing Setup

### 1. Add Frontend Testing

```bash
# apps/web/package.json - Add testing dependencies
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jest": "^29.0.0",
    "jest-environment-jsdom": "^29.0.0"
  }
}
```

### 2. Create Test Configuration

```javascript
// apps/web/jest.config.js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
}

module.exports = createJestConfig(customJestConfig)
```

## 🐳 Docker Improvements

### 1. Multi-stage Dockerfile

```dockerfile
# Dockerfile
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM python:3.11-slim AS backend-builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync
COPY . .
RUN uv run --project apps/api python -m build

FROM python:3.11-slim AS production
WORKDIR /app
COPY --from=backend-builder /app/dist/ ./dist/
COPY --from=frontend-builder /app/.next/ ./frontend/
EXPOSE 8000
CMD ["uv", "run", "--project", "apps/api", "uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Development Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE=http://localhost:8000
    depends_on:
      - api

  redis:
    image: redis/redis-stack:latest
    ports:
      - "6379:6379"
```

## 📋 Implementation Checklist

### Immediate (Today)
- [ ] Remove duplicate workspace config from package.json
- [ ] Fix API port configuration in frontend
- [ ] Add missing dev dependencies (concurrently, cross-env)
- [ ] Update build scripts for consistency

### This Week
- [ ] Create shared ESLint configuration
- [ ] Implement basic frontend testing
- [ ] Add TypeScript path mapping
- [ ] Create proper shared UI kit structure

### Next Week
- [ ] Set up CI/CD pipeline
- [ ] Implement Docker multi-stage builds
- [ ] Add comprehensive testing
- [ ] Create development documentation

## 🚀 Quick Start Commands

After implementing fixes:

```bash
# Install all dependencies
pnpm install
uv sync

# Start development environment
pnpm run dev

# Run tests
pnpm run test

# Build for production
pnpm run build

# Lint and typecheck
pnpm run lint
pnpm run typecheck
```

## 📊 Current vs Recommended Structure

### Current Issues:
- ❌ Duplicate workspace configurations
- ❌ Port mismatches (8000 vs 8002)
- ❌ Empty shared packages
- ❌ Inconsistent build scripts
- ❌ Missing frontend tests
- ❌ No CI/CD pipeline

### After Fixes:
- ✅ Single source of truth for workspaces
- ✅ Consistent port configuration
- ✅ Proper shared package structure
- ✅ Unified build and test commands
- ✅ Comprehensive testing setup
- ✅ Automated CI/CD pipeline
