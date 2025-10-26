# Render Deployment Guide

This guide walks you through deploying the Medication Leaflet QA System to Render.

## Prerequisites

- GitHub repository with your code
- Render account (free tier available)
- OpenAI API key
- Redis database (Render Redis or external)

## Deployment Options

### Option 1: Web Service (Recommended)

**Best for**: Simple deployment with external Redis

#### Step 1: Create Redis Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Redis"
3. Choose a name (e.g., `rag-health-redis`)
4. Select the free tier
5. Click "Create Redis"
6. Note the **External Redis URL** (you'll need this)

#### Step 2: Deploy Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `rag-health-api`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your deployment branch)

**Build & Deploy:**
- **Build Command**:
  ```bash
  pip install -r requirements.txt && pip install -e packages/py/core && pip install -e packages/py/retrieval && pip install -e apps/api
  ```
- **Start Command**:
  ```bash
  python start.py
  ```

**Environment Variables:**
```
OPENAI_API_KEY=sk-your-openai-key-here
REDIS_HOST=your-redis-host.render.com
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
WANDB_API_KEY=your-wandb-key (optional)
WANDB_PROJECT=rag-health-poc
WANDB_ENTITY=your-wandb-entity (optional)
```

#### Step 3: Deploy

1. Click "Create Web Service"
2. Wait for build to complete (5-10 minutes)
3. Your API will be available at `https://your-app-name.onrender.com`

### Option 2: Docker Service

**Best for**: Full control over environment

#### Step 1: Create Redis Database
(Same as Option 1, Step 1)

#### Step 2: Deploy Docker Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `rag-health-api`
- **Environment**: `Docker`
- **Region**: Choose closest to your users
- **Branch**: `main`

**Build & Deploy:**
- **Dockerfile Path**: `Dockerfile.render`
- **Docker Context Directory**: `.` (root)

**Environment Variables:**
(Same as Option 1)

#### Step 3: Deploy

1. Click "Create Web Service"
2. Wait for build to complete (10-15 minutes)
3. Your API will be available at `https://your-app-name.onrender.com`

## Post-Deployment Setup

### 1. Initialize the System

Once deployed, you need to initialize the Redis index and seed data:

```bash
# Create the search index
curl -X POST https://your-app-name.onrender.com/index/create

# Seed with default drugs (optional)
curl -X POST https://your-app-name.onrender.com/ingest/metformin
curl -X POST https://your-app-name.onrender.com/ingest/lisinopril
curl -X POST https://your-app-name.onrender.com/ingest/atorvastatin
```

### 2. Test the Deployment

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Ask a question
curl -X POST https://your-app-name.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the starting dose?", "drug": "metformin"}'

# Check stats
curl https://your-app-name.onrender.com/stats
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key for LLM and embeddings |
| `REDIS_HOST` | ✅ | localhost | Redis server hostname |
| `REDIS_PORT` | ✅ | 6379 | Redis server port |
| `REDIS_PASSWORD` | ❌ | - | Redis password (if required) |
| `WANDB_API_KEY` | ❌ | - | Weights & Biases API key for monitoring |
| `WANDB_PROJECT` | ❌ | rag-health-poc | W&B project name |
| `WANDB_ENTITY` | ❌ | - | W&B entity/username |
| `CHUNK_SIZE` | ❌ | 1536 | Text chunk size for processing |
| `CHUNK_OVERLAP` | ❌ | 150 | Overlap between chunks |
| `RETRIEVAL_TOP_K` | ❌ | 6 | Number of contexts to retrieve |
| `CONFIDENCE_THRESHOLD` | ❌ | 0.7 | Minimum confidence for answers |

## Monitoring & Maintenance

### Health Monitoring

- **Health Endpoint**: `GET /health` - Check Redis connectivity
- **Stats Endpoint**: `GET /stats` - View document count
- **Render Dashboard**: Monitor CPU, memory, and response times

### Scaling

- **Free Tier**: 750 hours/month, sleeps after 15 minutes of inactivity
- **Starter Plan**: $7/month - Always on, 512MB RAM
- **Standard Plan**: $25/month - 1GB RAM, better performance

### Data Persistence

- Redis data persists on Render Redis
- No additional backup needed for free tier
- Consider Redis Cloud for production workloads

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Python version (must be 3.11+)
   - Verify all dependencies in `requirements.txt`
   - Check build logs in Render dashboard

2. **Redis Connection Issues**
   - Verify Redis URL and credentials
   - Check Redis service is running
   - Test connection with Redis CLI

3. **OpenAI API Errors**
   - Verify API key is correct
   - Check API quota and rate limits
   - Monitor usage in OpenAI dashboard

4. **Memory Issues**
   - Upgrade to paid plan for more RAM
   - Optimize chunk sizes
   - Monitor memory usage in Render dashboard

### Debug Commands

```bash
# Check service logs
# (Available in Render dashboard under "Logs" tab)

# Test Redis connection
redis-cli -h your-redis-host -p 6379 ping

# Test API endpoints
curl -v https://your-app-name.onrender.com/health
```

## Cost Estimation

### Free Tier
- **Web Service**: 750 hours/month (sleeps after inactivity)
- **Redis**: 25MB storage, 30 connections
- **Total**: $0/month

### Starter Plan
- **Web Service**: $7/month (always on)
- **Redis**: $7/month (1GB storage)
- **Total**: ~$14/month

### Production Setup
- **Web Service**: $25/month (1GB RAM)
- **Redis**: $15/month (2GB storage)
- **Total**: ~$40/month

## Security Considerations

1. **API Keys**: Store in Render environment variables (encrypted)
2. **CORS**: Currently allows all origins - restrict for production
3. **Rate Limiting**: Consider adding rate limiting for production
4. **HTTPS**: Automatically provided by Render
5. **Redis Security**: Use Redis AUTH if needed

## Next Steps

1. **Custom Domain**: Add your own domain in Render settings
2. **Monitoring**: Set up alerts for health checks
3. **Backup**: Consider automated Redis backups
4. **CI/CD**: Set up automatic deployments from GitHub
5. **Scaling**: Monitor usage and upgrade plans as needed

## Support

- **Render Docs**: https://render.com/docs
- **Render Support**: Available in dashboard
- **Project Issues**: Create GitHub issues for bugs
