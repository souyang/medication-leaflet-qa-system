# 🚀 Quick Reference Card

## **Essential Commands**

```bash
# Setup (first time only)
just setup                    # Full environment setup

# Development
just dev                      # Start API + Frontend
just dev-api                  # API only (port 8000)
just dev-web                  # Frontend only (port 3001)

# Data
just seed                     # Ingest default drugs
just ingest aspirin           # Ingest specific drug
just ask "What is the dose?" metformin  # Test query

# Quality
just lint                     # Lint all code
just typecheck               # Type check all code
just test                    # Run all tests

# Health
just health                  # API health check
just stats                   # Redis stats
```

## **Key URLs**

- **API**: http://localhost:8000
- **Frontend**: http://localhost:3001
- **API Docs**: http://localhost:8000/docs
- **RedisInsight**: http://localhost:8001

## **Project Structure**

```
apps/
├── api/          # FastAPI backend
├── evals/        # W&B evaluation suite
└── web/          # Next.js frontend

packages/
├── js/ui-kit/    # Shared React components
└── py/
    ├── core/     # Business logic & types
    └── retrieval/ # Redis & embeddings
```

## **Tech Stack**

- **Backend**: FastAPI + LangGraph + Redis + OpenAI
- **Frontend**: Next.js + TypeScript + Tailwind + shadcn/ui
- **Tools**: uv (Python) + pnpm (Node.js) + Docker

## **Troubleshooting**

```bash
# Port conflicts
lsof -ti:8000 | xargs kill    # Kill API port
lsof -ti:3001 | xargs kill    # Kill frontend port

# Redis issues
just stop-redis && just dev-redis  # Restart Redis

# Python imports
cd apps/api && PYTHONPATH=. uv run python script.py

# Type checking
cd apps/api && uv run mypy .  # Check per project
```

## **Environment Variables**

```bash
# Required in .env
OPENAI_API_KEY=sk-...
WANDB_API_KEY=...
WANDB_ENTITY=...
REDIS_HOST=localhost
REDIS_PORT=6379
```

## **Deployment Commands**

```bash
# Local development
just up-fullstack  # Full-stack locally
just up            # Backend only locally

# Railway deployment (production)
just deploy        # Full-stack deployment
just deploy-backend # Backend only
```

## **Common Workflows**

### **Add New API Endpoint**
1. Add route in `apps/api/app/api.py`
2. Add types in `packages/py/core/rag_health_core/types.py`
3. Test with `just ask "test"`

### **Add New Frontend Page**
1. Create page in `apps/web/app/new-page/page.tsx`
2. Add API client in `apps/web/src/lib/fetch.ts`
3. Test with `pnpm --filter web dev`

### **Deploy to Production**
1. Run `just deploy` to deploy full-stack
2. Set environment variables in Railway dashboard
3. Test with `curl https://your-app.railway.app/health`

### **Debug Issues**
1. Check `just health` - API working?
2. Check `just stats` - Redis working?
3. Check logs in terminal where services are running
4. Test with `just ask "test" metformin`

## **Success Criteria**

- ✅ `just dev` starts both services
- ✅ `just health` returns 200 OK
- ✅ `just ask "What is metformin?" metformin` returns answer
- ✅ `just lint && just typecheck` passes
- ✅ `just test` passes

**🎯 You're ready to go!**
