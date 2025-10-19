# Monorepo Structure Audit Report

## Executive Summary

This audit evaluates the current monorepo structure for the Medication Leaflet Q&A system, which combines Python backend services (FastAPI) with a Next.js frontend. The structure is generally well-organized but has several areas for improvement in terms of consistency, scalability, and maintainability.

## Current Structure Analysis

### ✅ Strengths

1. **Clear Separation of Concerns**
   - Backend services in `apps/api` and `apps/evals`
   - Frontend in `apps/web`
   - Shared packages in `packages/py` and `packages/js`

2. **Proper Workspace Configuration**
   - Python: `uv` workspace with proper member definitions
   - Node.js: `pnpm` workspace with correct package definitions

3. **Type Safety**
   - Full TypeScript implementation in frontend
   - Python type hints with mypy strict mode

4. **Modern Tooling**
   - FastAPI with async support
   - Next.js 14 with App Router
   - Tailwind CSS + shadcn/ui

### ⚠️ Issues Identified

## 1. Package Management Inconsistencies

### Problem
- **Mixed package managers**: `uv` for Python, `pnpm` for Node.js
- **Duplicate configurations**: Both `package.json` and `pnpm-workspace.yaml` define workspaces
- **Missing shared JS packages**: `packages/js/ui-kit` is empty

### Impact
- Developer confusion about which tool to use
- Potential dependency conflicts
- Unused workspace definitions

### Recommendations
```bash
# Remove duplicate workspace definition from package.json
# Keep only pnpm-workspace.yaml for Node.js workspaces

# Implement shared UI kit
packages/js/ui-kit/
├── package.json
├── src/
│   ├── components/
│   ├── hooks/
│   └── utils/
└── tsconfig.json
```

## 2. Configuration Fragmentation

### Problem
- **Scattered configs**: ESLint, Prettier, TypeScript configs in multiple locations
- **Inconsistent tooling**: Different linting rules across packages
- **Missing shared configs**: No shared ESLint/Prettier configs for JS packages

### Impact
- Inconsistent code quality
- Duplicate configuration maintenance
- Developer experience friction

### Recommendations
```bash
# Create shared configs
packages/js/
├── eslint-config/          # Shared ESLint config
├── prettier-config/        # Shared Prettier config
├── typescript-config/      # Shared TypeScript config
└── ui-kit/                 # Shared UI components
```

## 3. Build and Deployment Pipeline

### Problem
- **No unified build system**: Separate build processes for Python and Node.js
- **Missing CI/CD configuration**: No GitHub Actions or similar
- **No Docker multi-stage builds**: Separate containers for each service

### Impact
- Complex deployment process
- No automated testing/quality gates
- Inconsistent environments

### Recommendations
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v2
      - run: uv sync
      - run: uv run pytest
      - run: uv run ruff check .
      - run: uv run mypy .

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: pnpm --filter web typecheck
      - run: pnpm --filter web lint
      - run: pnpm --filter web build
```

## 4. Environment and Secrets Management

### Problem
- **Hardcoded ports**: API on 8002, Web on 3001
- **Missing environment validation**: No schema validation for env vars
- **No secrets management**: API keys in plain text

### Impact
- Environment-specific issues
- Security vulnerabilities
- Deployment complexity

### Recommendations
```typescript
// packages/js/shared-config/src/env.ts
import { z } from 'zod';

export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  API_BASE_URL: z.string().url(),
  OPENAI_API_KEY: z.string().min(1),
  REDIS_URL: z.string().url(),
});

export type Env = z.infer<typeof envSchema>;
```

## 5. Testing Strategy

### Problem
- **Limited test coverage**: Only basic Python tests
- **No frontend tests**: Missing React component tests
- **No integration tests**: No end-to-end testing

### Impact
- Low confidence in deployments
- Regression risks
- Poor developer experience

### Recommendations
```bash
# Add comprehensive testing
apps/web/
├── __tests__/
│   ├── components/
│   ├── pages/
│   └── utils/
├── cypress/                 # E2E tests
└── jest.config.js

tests/
├── unit/                   # Unit tests
├── integration/            # Integration tests
└── e2e/                   # End-to-end tests
```

## 6. Documentation and Developer Experience

### Problem
- **Scattered documentation**: Multiple README files
- **Missing API documentation**: No OpenAPI/Swagger setup
- **No development guides**: Unclear onboarding process

### Impact
- Poor developer onboarding
- Inconsistent development practices
- Maintenance overhead

### Recommendations
```bash
# Centralized documentation
docs/
├── README.md              # Main documentation
├── api/                   # API documentation
├── frontend/              # Frontend guides
├── deployment/            # Deployment guides
└── development/           # Development setup
```

## Recommended Improvements

### Phase 1: Immediate Fixes (1-2 weeks)

1. **Consolidate Package Management**
   ```bash
   # Remove duplicate workspace config
   # Implement shared JS packages
   # Standardize build scripts
   ```

2. **Fix Configuration Issues**
   ```bash
   # Create shared configs
   # Standardize linting rules
   # Fix port configurations
   ```

3. **Add Basic Testing**
   ```bash
   # Add frontend unit tests
   # Improve Python test coverage
   # Add basic integration tests
   ```

### Phase 2: Infrastructure (2-4 weeks)

1. **CI/CD Pipeline**
   ```bash
   # GitHub Actions workflow
   # Automated testing
   # Quality gates
   ```

2. **Docker Optimization**
   ```bash
   # Multi-stage builds
   # Development containers
   # Production optimization
   ```

3. **Monitoring and Observability**
   ```bash
   # Structured logging
   # Health checks
   # Performance monitoring
   ```

### Phase 3: Advanced Features (1-2 months)

1. **Shared Component Library**
   ```bash
   # Reusable UI components
   # Design system
   # Storybook documentation
   ```

2. **Advanced Testing**
   ```bash
   # E2E testing with Playwright
   # Visual regression testing
   # Performance testing
   ```

3. **Developer Experience**
   ```bash
   # Development containers
   # Hot reloading
   # Debugging tools
   ```

## File Structure Recommendations

```
medication-leaflet-qa-system/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy.yml
│       └── release.yml
├── apps/
│   ├── api/                    # FastAPI backend
│   ├── evals/                  # Evaluation service
│   └── web/                    # Next.js frontend
├── packages/
│   ├── js/
│   │   ├── eslint-config/      # Shared ESLint config
│   │   ├── prettier-config/    # Shared Prettier config
│   │   ├── typescript-config/  # Shared TypeScript config
│   │   └── ui-kit/             # Shared UI components
│   └── py/
│       ├── core/               # Core business logic
│       └── retrieval/          # Retrieval components
├── docs/                       # Centralized documentation
├── infra/                      # Infrastructure as code
├── tests/                      # Shared test utilities
├── .env.example               # Environment template
├── docker-compose.yml         # Development environment
├── Dockerfile                 # Multi-stage production build
├── package.json               # Root package.json (minimal)
├── pnpm-workspace.yaml        # pnpm workspace config
├── pyproject.toml             # Python workspace config
└── README.md                  # Main documentation
```

## Priority Matrix

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Package Management | High | Low | 🔴 Critical |
| Configuration | Medium | Low | 🟡 High |
| Testing | High | Medium | 🟡 High |
| CI/CD | Medium | Medium | 🟢 Medium |
| Documentation | Low | Low | 🟢 Medium |
| Shared Components | Low | High | 🔵 Low |

## Conclusion

The current monorepo structure provides a solid foundation but requires immediate attention to package management and configuration consistency. The recommended improvements will significantly enhance developer experience, code quality, and deployment reliability.

**Next Steps:**
1. Implement Phase 1 fixes immediately
2. Plan Phase 2 infrastructure improvements
3. Consider Phase 3 features based on team needs and timeline
