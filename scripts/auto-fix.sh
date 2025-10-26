#!/bin/bash
# Auto-fix script for code formatting and linting

set -e

echo "🔧 Running auto-fix for code formatting and linting..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this script from the project root"
    exit 1
fi

echo "📝 Formatting code with ruff..."
uv run ruff format .

echo "🔍 Running linting with auto-fix..."
uv run ruff check --fix .

echo "🔍 Running linting with unsafe fixes..."
uv run ruff check --fix --unsafe-fixes .

echo "✅ Auto-fix complete!"
echo ""
echo "📋 Summary:"
echo "   - Code formatted with ruff"
echo "   - Linting issues fixed automatically"
echo "   - Unsafe fixes applied"
echo ""
echo "💡 You can also use these commands:"
echo "   - just fix-all          # Format and fix all issues"
echo "   - just lint-fix         # Fix safe linting issues"
echo "   - just lint-fix-unsafe  # Fix all linting issues"
echo "   - just fmt              # Format code only"
echo "   - just lint             # Check for issues only"
