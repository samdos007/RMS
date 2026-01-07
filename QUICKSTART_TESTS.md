# Quick Start: Running Tests

## 1. Backend Tests (5 minutes)

```bash
# Navigate to backend
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest

# Expected output:
# ===== test session starts =====
# collected 65+ items
#
# tests/test_earnings.py ..................... [ 38%]
# tests/test_guidance.py .................... [ 69%]
# tests/test_folders.py .....                [ 77%]
# tests/test_integration.py ...............   [100%]
#
# ===== 65+ passed in X.XXs =====
```

### If Tests Fail:

1. Check database is clean: `rm data/rms.db` (if exists)
2. Ensure all migrations ran: `alembic upgrade head`
3. Check Python version: `python --version` (should be 3.11+)

## 2. Frontend Tests (5 minutes)

```bash
# Navigate to frontend
cd frontend

# Install NEW dependencies (REQUIRED)
npm install

# Run all tests
npm test

# Expected output:
# ✓ src/tests/formatting.test.ts (30+ tests)
# ✓ src/tests/api.test.ts (15+ tests)
#
# Test Files  2 passed (2)
#      Tests  45+ passed (45+)
```

### If Tests Fail:

1. Ensure dependencies installed: `npm install`
2. Clear cache: `rm -rf node_modules && npm install`
3. Check Node version: `node --version` (should be 18+)

## 3. Quick Verification

### Backend

```bash
cd backend

# Run only earnings tests
pytest tests/test_earnings.py

# Run with coverage
pytest --cov=app

# Run only unit tests
pytest -m unit
```

### Frontend

```bash
cd frontend

# Run only formatting tests
npm test formatting.test.ts

# Run with UI (opens browser)
npm run test:ui

# Run with coverage
npm run test:coverage
```

## Common Issues

### Issue: "Module not found"
**Solution:** Install dependencies
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Issue: "Database locked" (Backend)
**Solution:** Stop any running servers
```bash
# Stop backend server
# Ctrl+C or kill uvicorn process
```

### Issue: Frontend tests not found
**Solution:** Make sure you're in the frontend directory
```bash
cd frontend
npm test
```

## What to Look For

### ✅ Success Indicators:

**Backend:**
```
====== 65+ passed in X.XXs ======
```

**Frontend:**
```
Test Files  2 passed (2)
     Tests  45+ passed (45+)
```

### ❌ Failure Indicators:

Look for:
- `FAILED tests/test_*.py` - Backend test failed
- `✗ src/tests/*.test.ts` - Frontend test failed
- Red text in output
- `AssertionError` or `Error` messages

## Next Steps

1. **Read Full Documentation:** See `TESTING.md`
2. **Add More Tests:** See README files in test directories
3. **Set Up CI/CD:** Add to GitHub Actions
4. **Pre-commit Hooks:** Run tests before commits

## Need Help?

Check these files:
- `TESTING.md` - Complete testing guide
- `TEST_SUMMARY.md` - What was built
- `backend/tests/README.md` - Backend specifics
- `frontend/src/tests/README.md` - Frontend specifics
