#!/bin/bash
# Deployment script for Render

set -e

echo "🚀 Preparing deployment to Render..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this script from the project root"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Run the deployment preparation first."
    exit 1
fi

# Check if start.py exists
if [ ! -f "start.py" ]; then
    echo "❌ Error: start.py not found. Run the deployment preparation first."
    exit 1
fi

echo "✅ Project structure looks good"

# Check for required environment variables
echo "🔍 Checking environment variables..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "   You'll need to set this in Render dashboard"
fi

if [ -z "$REDIS_HOST" ]; then
    echo "⚠️  Warning: REDIS_HOST not set"
    echo "   You'll need to create a Redis database in Render"
fi

echo "📋 Deployment Checklist:"
echo "   1. ✅ Code is ready"
echo "   2. ✅ requirements.txt created"
echo "   3. ✅ start.py created"
echo "   4. ✅ Dockerfile.render created"
echo ""
echo "🎯 Next Steps:"
echo "   1. Push your code to GitHub"
echo "   2. Go to https://dashboard.render.com"
echo "   3. Create a new Web Service"
echo "   4. Connect your GitHub repository"
echo "   5. Use these settings:"
echo "      - Build Command: pip install -r requirements.txt && pip install -e packages/py/core && pip install -e packages/py/retrieval && pip install -e apps/api"
echo "      - Start Command: python start.py"
echo "   6. Set environment variables in Render dashboard"
echo "   7. Deploy!"
echo ""
echo "📖 For detailed instructions, see RENDER_DEPLOYMENT.md"
echo ""
echo "🔗 Useful URLs:"
echo "   - Render Dashboard: https://dashboard.render.com"
echo "   - Create Redis: https://dashboard.render.com/new/redis"
echo "   - Create Web Service: https://dashboard.render.com/new/web-service"
