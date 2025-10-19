# 🚀 Railway Deployment Guide

## 🎯 **Railway: The Complete Solution**

Railway is the perfect platform for deploying your RAG system because it provides:
- ✅ **Full-Stack Support**: Frontend + Backend + Database
- ✅ **Zero Configuration**: Deploy from GitHub
- ✅ **Managed Services**: Redis included
- ✅ **Auto-Scaling**: Scales based on traffic
- ✅ **SSL**: Automatic HTTPS
- ✅ **Monitoring**: Built-in metrics and logs

---

## 🚀 **Quick Deploy (5 minutes)**

### **1. Install Railway CLI**
```bash
npm install -g @railway/cli
```

### **2. Login to Railway**
```bash
railway login
```

### **3. Deploy Full-Stack**
```bash
just deploy
```

### **4. Set Environment Variables**
```bash
# Railway will prompt you to set these:
OPENAI_API_KEY=sk-your-openai-key
WANDB_API_KEY=your-wandb-key
WANDB_ENTITY=your-wandb-entity
```

### **5. Access Your App**
Railway will give you a URL like: `https://your-app.railway.app`

---

## 📊 **What Gets Deployed**

### **Full-Stack Deployment:**
- ✅ **Frontend**: Next.js web app (main URL)
- ✅ **Backend**: FastAPI API (internal service)
- ✅ **Database**: Managed Redis
- ✅ **SSL**: Automatic HTTPS
- ✅ **Monitoring**: Built-in metrics

### **Backend Only Deployment:**
- ✅ **Backend**: FastAPI API (main URL)
- ✅ **Database**: Managed Redis
- ✅ **SSL**: Automatic HTTPS
- ✅ **Monitoring**: Built-in metrics

---

## 🔧 **Deployment Commands**

### **Full-Stack (Recommended)**
```bash
just deploy
# or
just deploy-fullstack
```

### **Backend Only**
```bash
just deploy-backend
```

### **Local Development**
```bash
just up-fullstack  # Full-stack locally
just up            # Backend only locally
```

---

## 📋 **Environment Variables**

Set these in Railway dashboard or CLI:

### **Required:**
```bash
OPENAI_API_KEY=sk-your-openai-key
WANDB_API_KEY=your-wandb-key
WANDB_ENTITY=your-wandb-entity
```

### **Optional:**
```bash
REDIS_HOST=redis
REDIS_PORT=6379
NEXT_PUBLIC_API_BASE=https://your-app.railway.app
NEXT_PUBLIC_APP_NAME=Medication Leaflet Q&A
```

---

## 🎯 **Deployment Options**

### **Option 1: Full-Stack (Recommended)**
```bash
just deploy
```

**What you get:**
- **Main App**: `https://your-app.railway.app`
  - ✅ Chat interface
  - ✅ Drug ingestion form
  - ✅ Evaluation triggers
  - ✅ Health monitoring
- **API**: `https://your-app.railway.app/api/*`
  - ✅ `/ask` endpoint
  - ✅ `/ingest` endpoint
  - ✅ `/health` endpoint
- **Database**: Managed Redis

### **Option 2: Backend Only**
```bash
just deploy-backend
```

**What you get:**
- **API**: `https://your-app.railway.app`
  - ✅ `/ask` endpoint
  - ✅ `/ingest` endpoint
  - ✅ `/health` endpoint
  - ✅ `/docs` (Swagger UI)
- **Database**: Managed Redis

---

## 🔍 **After Deployment**

### **1. Verify Deployment**
```bash
# Check if your app is running
curl https://your-app.railway.app/health
```

### **2. Populate Data**
```bash
# In Railway dashboard, run:
cd apps/api && PYTHONPATH=. python scripts/seed_ingest.py --create-index --drop-existing
```

### **3. Test the System**
```bash
# Test API
curl -X POST https://your-app.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is metformin?", "drug": "metformin"}'
```

---

## 📊 **Railway Dashboard**

After deployment, you can monitor your app in the Railway dashboard:

### **Services:**
- **Frontend**: Next.js web app
- **Backend**: FastAPI API
- **Database**: Redis

### **Metrics:**
- **Requests**: API call volume
- **Response Time**: API performance
- **Errors**: Error rates and logs
- **Resources**: CPU and memory usage

### **Logs:**
- **Real-time**: Live application logs
- **Search**: Filter and search logs
- **Alerts**: Set up notifications

---

## 🚀 **Scaling**

### **Auto-Scaling:**
Railway automatically scales your services based on traffic:
- **Low Traffic**: Minimal resources
- **High Traffic**: More resources allocated
- **Peak Traffic**: Maximum resources

### **Manual Scaling:**
You can also manually adjust resources in the Railway dashboard.

---

## 💰 **Pricing**

### **Free Tier:**
- ✅ **$5 credit** per month
- ✅ **Perfect for development** and small projects
- ✅ **All features included**

### **Pro Plan:**
- ✅ **$5-20/month** for production
- ✅ **Higher resource limits**
- ✅ **Priority support**

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. Environment Variables Not Set**
```bash
# Set in Railway dashboard or CLI
railway variables set OPENAI_API_KEY=sk-your-key
```

#### **2. Build Failures**
```bash
# Check logs in Railway dashboard
# Common issues: missing dependencies, build errors
```

#### **3. API Not Responding**
```bash
# Check health endpoint
curl https://your-app.railway.app/health
```

#### **4. Redis Connection Issues**
```bash
# Railway provides Redis automatically
# Check REDIS_HOST and REDIS_PORT variables
```

---

## 🎉 **Success Checklist**

After deployment, verify:
- [ ] **App is accessible**: `https://your-app.railway.app`
- [ ] **Health check passes**: `/health` endpoint responds
- [ ] **API works**: `/ask` endpoint responds
- [ ] **Data is populated**: Run seed script
- [ ] **Frontend loads**: Web interface works
- [ ] **SSL is working**: HTTPS is enabled

---

## 🚀 **Next Steps**

1. **Deploy**: `just deploy`
2. **Set Variables**: Add your API keys
3. **Populate Data**: Run seed script
4. **Test**: Verify everything works
5. **Monitor**: Check Railway dashboard
6. **Scale**: Adjust resources as needed

---

**🎯 Railway is the perfect platform for your RAG system - simple, powerful, and production-ready!**
