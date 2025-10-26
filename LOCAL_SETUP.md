# 🚀 Local Development Setup

## 🎯 **Quick Start (5 minutes)**

### **Step 1: Prerequisites Check**
```bash
# Check if you have the required tools
python --version  # Should be 3.11+
docker --version  # Should be installed
uv --version      # Should be installed
just --version    # Should be installed
pnpm --version    # Should be installed
```

### **Step 2: Environment Setup**
```bash
# 1. Create environment file
cp env.example .env

# 2. Edit .env and add your API keys
# Required: OPENAI_API_KEY=sk-your-openai-key
# Optional: WANDB_API_KEY, WANDB_ENTITY
```

### **Step 3: Full Setup (One Command)**
```bash
# This will install all dependencies, start Redis, and seed data
just setup
```

### **Step 4: Start Development**
```bash
# Start full stack (API + Frontend)
just dev

# Or start services individually:
just dev-api    # API only on http://localhost:8000
just dev-web    # Frontend only on http://localhost:3001
```

---

## 🔧 **Step-by-Step Setup**

### **1. Install Dependencies**

#### **Python Dependencies:**
```bash
# Install Python dependencies using uv
uv sync
```

#### **Node.js Dependencies:**
```bash
# Install Node.js dependencies using pnpm
pnpm install
```

### **2. Start Infrastructure**

#### **Start Redis:**
```bash
# Start Redis Stack in Docker
just dev-redis

# Verify Redis is running
docker ps | grep redis
```

#### **Create Redis Index:**
```bash
# Create the vector search index
just create-index
```

### **3. Seed Data**

#### **Ingest Default Drugs:**
```bash
# Ingest 5 default drugs (metformin, lisinopril, etc.)
just seed
```

#### **Verify Data:**
```bash
# Check if data was ingested
just stats
```

### **4. Start Services**

#### **Option A: Full Stack (Recommended)**
```bash
# Start both API and frontend
just dev
```

#### **Option B: Individual Services**
```bash
# Terminal 1: Start API
just dev-api

# Terminal 2: Start Frontend
just dev-web
```

---

## 🌐 **Access Your Local Services**

### **API Service:**
- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Stats**: http://localhost:8000/stats

### **Frontend Service:**
- **URL**: http://localhost:3001
- **Features**: Chat interface, drug ingestion, evaluations

### **Redis Stack:**
- **Redis**: localhost:6379
- **RedisInsight**: http://localhost:8001

---

## 🧪 **Test Your Setup**

### **1. Health Check**
```bash
# Check if API is running
curl http://localhost:8000/health
# Expected: {"ok": true}
```

### **2. Ask a Question**
```bash
# Ask a question about a drug
just ask Q="What is the starting dose?" DRUG="metformin"
```

### **3. Ingest New Drug**
```bash
# Ingest a new drug
just ingest DRUG="aspirin"
```

### **4. Run Evaluations**
```bash
# Run W&B evaluations
just eval
```

---

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **1. Redis Connection Failed**
```bash
# Check if Redis is running
docker ps | grep redis

# Restart Redis if needed
just stop-redis
just dev-redis
```

#### **2. API Import Errors**
```bash
# Make sure you're in the right directory
cd /path/to/Medication-Leaflet-QA-System

# Check Python path
echo $PYTHONPATH

# Reinstall dependencies
uv sync
```

#### **3. Frontend Not Loading**
```bash
# Check if pnpm is installed
pnpm --version

# Reinstall Node.js dependencies
pnpm install

# Check if port 3001 is available
lsof -i :3001
```

#### **4. Environment Variables**
```bash
# Check if .env file exists
ls -la .env

# Verify API key is set
grep OPENAI_API_KEY .env
```

---

## 📋 **Available Commands**

### **Development:**
```bash
just dev          # Start full stack
just dev-api      # Start API only
just dev-web      # Start frontend only
just dev-redis    # Start Redis only
```

### **Data Management:**
```bash
just seed         # Ingest default drugs
just ingest DRUG="aspirin"  # Ingest specific drug
just create-index # Create Redis index
just stats        # Show database stats
```

### **Testing:**
```bash
just ask Q="question" DRUG="drug"  # Ask a question
just health       # Check API health
just eval         # Run evaluations
```

### **Infrastructure:**
```bash
just setup        # Full setup (deps + Redis + data)
just stop-redis   # Stop Redis
just clean        # Clean cache files
```

---

## 🎯 **Development Workflow**

### **1. Daily Development:**
```bash
# Start your development session
just dev-redis    # Start Redis
just dev          # Start full stack
```

### **2. Testing Changes:**
```bash
# Test API changes
just health       # Check health
just ask Q="test question" DRUG="metformin"

# Test frontend changes
# Visit http://localhost:3001
```

### **3. Adding New Data:**
```bash
# Ingest new drugs
just ingest DRUG="new-drug-name"

# Verify ingestion
just stats
```

### **4. Running Evaluations:**
```bash
# Run W&B evaluations
just eval

# Check evaluation results in W&B dashboard
```

---

## 🚀 **Next Steps**

### **After Local Setup:**
1. **✅ Test all functionality** locally
2. **✅ Verify API responses** are correct
3. **✅ Check frontend** loads and works
4. **✅ Run evaluations** to ensure quality
5. **🚀 Deploy to production** (Render recommended)

### **Production Deployment:**
```bash
# After local testing, deploy to Render
just deploy-render
```

---

## 🎉 **Success Indicators**

### **✅ Everything Working:**
- **API Health**: `curl http://localhost:8000/health` returns `{"ok": true}`
- **Frontend**: http://localhost:3001 loads without errors
- **Redis**: `docker ps | grep redis` shows running container
- **Data**: `just stats` shows ingested drugs
- **Queries**: `just ask` returns proper responses

### **🎯 You're Ready for Production!**

Once everything works locally, you can confidently deploy to production using Render or any other platform.

---

**🎯 Local development is the best way to test everything before deployment!**
