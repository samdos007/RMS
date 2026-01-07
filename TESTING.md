# RMS Testing Guide

Comprehensive testing documentation for the Research Management System.

## Overview

This project has comprehensive test coverage for both backend and frontend, focusing on the earnings and guidance tracking features.

### Test Statistics

**Backend:**
- 4 test files
- 50+ unit tests
- 15+ integration tests
- Coverage: Earnings, Guidance, Folders, Integration workflows

**Frontend:**
- 2 test files
- 40+ unit tests
- Coverage: Value formatting, API clients, data conversion

## Quick Start

### Backend Tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

### Frontend Tests

```bash
cd frontend
npm install
npm test
```

## Backend Testing

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_earnings.py

# Specific test
pytest tests/test_earnings.py::TestEarningsCRUD::test_create_earnings_success

# With coverage
pytest --cov=app --cov-report=html

# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration
```

### Test Files

| File | Purpose | Tests |
|------|---------|-------|
| `test_earnings.py` | Earnings CRUD, calculations, validations | 25+ tests |
| `test_guidance.py` | Guidance CRUD, calculations, metrics | 20+ tests |
| `test_folders.py` | Folder tickers property | 5+ tests |
| `test_integration.py` | Cross-module workflows, cascades | 15+ tests |

### Key Test Categories

**Earnings Tests:**
- ✅ Create earnings (quarterly & annual)
- ✅ Update earnings with actuals
- ✅ Delete earnings
- ✅ Prevent duplicate earnings
- ✅ Ticker validation (must belong to folder)
- ✅ EPS surprise calculations
- ✅ Revenue surprise calculations
- ✅ EBITDA surprise calculations
- ✅ FCF surprise calculations
- ✅ Pair folder support

**Guidance Tests:**
- ✅ Create guidance (range & point estimates)
- ✅ Update guidance with actuals
- ✅ Delete guidance
- ✅ Midpoint calculations
- ✅ Vs-guidance percentage calculations
- ✅ All metric types (EPS, Revenue, EBITDA, FCF, OTHER)
- ✅ Ticker validation
- ✅ Pair folder support

**Integration Tests:**
- ✅ Folder deletion cascades to earnings
- ✅ Folder deletion cascades to guidance
- ✅ Complete earnings cycle workflow
- ✅ Pair folder workflows

### Fixtures

Defined in `conftest.py`:
```python
db                      # Fresh test database
test_user               # Authenticated test user
client                  # Test client with auth
sample_folder_data      # Single folder data
sample_pair_folder_data # Pair folder data
```

## Frontend Testing

### Running Tests

```bash
# All tests
npm test

# Watch mode
npm test -- --watch

# With UI
npm run test:ui

# With coverage
npm run test:coverage

# Specific file
npm test formatting.test.ts
```

### Test Files

| File | Purpose | Tests |
|------|---------|-------|
| `formatting.test.ts` | Value formatting and conversions | 30+ tests |
| `api.test.ts` | API client calls and data structures | 15+ tests |

### Key Test Categories

**Formatting Tests:**
- ✅ EPS formatting ($X.XX)
- ✅ Revenue/EBITDA/FCF formatting ($X.XM millions)
- ✅ Millions → raw conversion (multiply by 1e6)
- ✅ Raw → millions conversion (divide by 1e6)
- ✅ Null/undefined handling
- ✅ Surprise percentage calculations
- ✅ Guidance midpoint calculations
- ✅ Edge cases (large/small/zero values)

**API Tests:**
- ✅ Earnings API endpoints
- ✅ Guidance API endpoints
- ✅ Data structure validation
- ✅ Query parameter handling
- ✅ Conversion logic verification

## Critical: Data Conversion

### The Million Dollar Bug 💰

The most critical aspect of the system is the **conversion between display (millions) and storage (raw values)**:

**Storage (Database):**
```
Revenue: 95000000000 (raw)
EBITDA:  30000000000 (raw)
FCF:     25000000000 (raw)
EPS:     2.48 (no conversion)
```

**Display (UI):**
```
Revenue: $95000.0M (95000000000 / 1e6)
EBITDA:  $30000.0M (30000000000 / 1e6)
FCF:     $25000.0M (25000000000 / 1e6)
EPS:     $2.48 (no conversion)
```

**User Input:**
```typescript
// User enters 95000 (millions)
const userInput = 95000;
const forStorage = userInput * 1e6;  // 95000000000
```

**Reading from API:**
```typescript
// API returns 95000000000 (raw)
const apiValue = 95000000000;
const forDisplay = apiValue / 1e6;  // 95000
```

### Tests Ensure This Works

Both `formatting.test.ts` and `api.test.ts` extensively test these conversions to prevent bugs.

## Test Coverage

### What's Tested

✅ **Backend:**
- All CRUD operations
- All surprise calculations
- Ticker validation
- Cascade deletion
- Duplicate prevention
- Workflow scenarios

✅ **Frontend:**
- Value formatting
- Conversion logic
- API calls
- Data structures
- Edge cases

### What's NOT Tested (Yet)

❌ **Backend:**
- yfinance fetch integration (requires mocking)
- CSV import/export
- Auth edge cases

❌ **Frontend:**
- Component rendering
- User interactions
- Form validation
- Error UI states

## Adding New Tests

### Backend

1. Add test to appropriate file in `backend/tests/`
2. Use pytest fixtures from `conftest.py`
3. Mark as `@pytest.mark.unit` or `@pytest.mark.integration`
4. Name clearly: `test_<action>_<scenario>`

### Frontend

1. Add test to `frontend/src/tests/`
2. Use vitest `describe` and `it` blocks
3. Import from `test-utils.tsx` for components
4. Test both happy path and edge cases

## Continuous Integration

### Pre-commit

```bash
# Run before committing
cd backend && pytest
cd frontend && npm test
```

### CI Pipeline (Future)

```yaml
# .github/workflows/test.yml
- name: Backend Tests
  run: cd backend && pytest --cov

- name: Frontend Tests
  run: cd frontend && npm test -- --coverage
```

## Debugging Failed Tests

### Backend

```bash
# Verbose output
pytest -v

# Stop at first failure
pytest -x

# Print statements
pytest -s

# Debug specific test
pytest --pdb tests/test_earnings.py::test_name
```

### Frontend

```bash
# Verbose output
npm test -- --reporter=verbose

# Watch single file
npm test -- --watch formatting.test.ts

# Debug in browser
npm run test:ui
```

## Test Data

### Sample Folder
```json
{
  "type": "SINGLE",
  "ticker_primary": "AAPL",
  "description": "Apple Inc.",
  "tags": ["tech", "large-cap"]
}
```

### Sample Earnings
```json
{
  "folder_id": "...",
  "ticker": "AAPL",
  "period_type": "QUARTERLY",
  "fiscal_quarter": "2024-Q4",
  "estimate_eps": 2.35,
  "actual_eps": 2.48,
  "estimate_rev": 95000000000,
  "actual_rev": 96000000000
}
```

### Sample Guidance
```json
{
  "folder_id": "...",
  "ticker": "AAPL",
  "period": "2025-Q1",
  "metric": "REVENUE",
  "guidance_period": "2024-Q4",
  "guidance_low": 94000000000,
  "guidance_high": 96000000000
}
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Maintenance

Tests should be updated when:
- Adding new features
- Changing data models
- Modifying calculations
- Updating API endpoints
- Fixing bugs (add regression test)

---

**Need Help?** Check the README files in:
- `backend/tests/README.md`
- `frontend/src/tests/README.md`
