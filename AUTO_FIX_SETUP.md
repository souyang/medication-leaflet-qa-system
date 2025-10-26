# Auto-Fix Setup Guide

This project now has comprehensive auto-fix capabilities for code formatting and linting.

## 🚀 Quick Start

### Automatic Fixes
```bash
# Fix all issues automatically
just fix-all

# Or use the script
./scripts/auto-fix.sh
```

### Individual Commands
```bash
# Format code only
just fmt

# Fix safe linting issues
just lint-fix

# Fix all linting issues (including unsafe)
just lint-fix-unsafe

# Check for issues without fixing
just lint
```

## 🔧 What's Included

### 1. **Ruff Auto-Fix**
- **Formatting**: Automatic code formatting
- **Import sorting**: Organizes imports correctly
- **Linting fixes**: Fixes safe issues automatically
- **Unsafe fixes**: Fixes more complex issues (use with caution)

### 2. **Pre-commit Hooks**
- Automatically runs fixes before commits
- Prevents bad code from being committed
- Install with: `just install-hooks`

### 3. **VS Code Integration**
- Auto-fix on save enabled
- Ruff extension recommended
- Settings in `.vscode/settings.json`

### 4. **Justfile Commands**
- `just fix-all` - Format and fix everything
- `just lint-fix` - Fix safe issues only
- `just lint-fix-unsafe` - Fix all issues
- `just fmt` - Format code only
- `just lint` - Check issues only

## 📁 Files Created/Updated

### New Files:
- `scripts/auto-fix.sh` - Comprehensive auto-fix script
- `.vscode/settings.json` - VS Code auto-fix settings
- `AUTO_FIX_SETUP.md` - This guide

### Updated Files:
- `Justfile` - Added auto-fix commands
- `start.py` - Fixed linting issues (replaced print with logging)
- `.pre-commit-config.yaml` - Already had auto-fix enabled

## 🎯 Usage Examples

### Before Committing
```bash
# Run auto-fix before committing
just fix-all
git add .
git commit -m "Your commit message"
```

### VS Code Users
1. Install the Ruff extension
2. Auto-fix will run on save
3. Manual fix: `Ctrl+Shift+P` → "Ruff: Fix all auto-fixable problems"

### CI/CD Integration
```bash
# In your CI pipeline
just lint  # Check for issues (fails if issues found)
just fmt   # Format code
```

## 🔍 What Gets Fixed

### Automatic Fixes:
- ✅ Import organization
- ✅ Unused imports removal
- ✅ Code formatting
- ✅ Simple syntax issues
- ✅ Style violations

### Manual Review Needed:
- ⚠️ Complex logic changes
- ⚠️ Variable name changes
- ⚠️ Function signature changes

## 🚨 Safety Notes

### Safe Fixes (`--fix`)
- Import organization
- Code formatting
- Simple syntax fixes
- Style improvements

### Unsafe Fixes (`--unsafe-fixes`)
- Variable renaming
- Function signature changes
- Complex logic modifications
- **Review carefully before committing**

## 🛠️ Troubleshooting

### Common Issues

1. **Pre-commit fails**
   ```bash
   just install-hooks  # Reinstall hooks
   ```

2. **VS Code not auto-fixing**
   - Install Ruff extension
   - Check `.vscode/settings.json` exists
   - Restart VS Code

3. **Ruff not found**
   ```bash
   uv sync  # Reinstall dependencies
   ```

4. **Conflicting formatters**
   - Disable other Python formatters
   - Use only Ruff for consistency

### Debug Commands
```bash
# Check what would be fixed
just lint

# See detailed output
uv run ruff check --verbose .

# Check specific file
uv run ruff check path/to/file.py
```

## 📊 Benefits

- ✅ **Consistent code style** across the project
- ✅ **Faster development** with automatic fixes
- ✅ **Fewer code review comments** about style
- ✅ **Better code quality** with automatic improvements
- ✅ **Team consistency** with shared configuration

## 🔄 Workflow Integration

### Recommended Workflow:
1. **Write code** normally
2. **Save file** (auto-fix runs in VS Code)
3. **Commit** (pre-commit hooks run)
4. **Push** (CI checks pass)

### Manual Workflow:
1. **Write code**
2. **Run** `just fix-all`
3. **Review** changes
4. **Commit** and push

## 📚 Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pre-commit Hooks](https://pre-commit.com/)
- [VS Code Ruff Extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 🎉 Success!

Your project now has comprehensive auto-fix capabilities! All code will be automatically formatted and linted, ensuring consistency and quality across your codebase.
