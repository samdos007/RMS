# Backend Tests

Comprehensive test suite for the RMS backend application.

## Running Tests

```bash
# Run all tests
cd backend
pytest

# Run specific test file
pytest tests/test_earnings.py

# Run specific test class
pytest tests/test_earnings.py::TestEarningsCRUD

# Run specific test
pytest tests/test_earnings.py::TestEarningsCRUD::test_create_earnings_success

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x
```

## Test Organization

### test_earnings.py
- **TestEarningsCRUD**: CRUD operations for earnings records
- **TestEarningsCalculations**: Surprise percentage calculations for all metrics
- **TestEarningsPairFolder**: Earnings with pair folders

### test_guidance.py
- **TestGuidanceCRUD**: CRUD operations for guidance records
- **TestGuidanceCalculations**: Midpoint and vs-guidance calculations
- **TestGuidanceMetrics**: Different metric types (EPS, Revenue, EBITDA, FCF, OTHER)

### test_folders.py
- **TestFolderTickers**: Tickers property for single and pair folders

### test_integration.py
- **TestEarningsFolderIntegration**: Folder deletion cascades, ticker validation
- **TestGuidanceFolderIntegration**: Folder deletion cascades, ticker validation
- **TestEarningsGuidanceWorkflow**: Complete realistic workflows

## Test Coverage

Current test coverage focuses on:
- ✅ Earnings CRUD operations
- ✅ Guidance CRUD operations
- ✅ All surprise calculations (EPS, Revenue, EBITDA, FCF)
- ✅ Ticker validation for single and pair folders
- ✅ Cascade deletion
- ✅ Complete earnings cycle workflows

## Fixtures

Defined in `conftest.py`:
- `db`: Fresh database for each test
- `test_user`: Test user for authentication
- `client`: Test client with auth and DB overrides
- `sample_folder_data`: Sample single folder data
- `sample_pair_folder_data`: Sample pair folder data

## Adding New Tests

1. Create test file: `test_<feature>.py`
2. Import pytest and fixtures
3. Create test classes with descriptive names
4. Use markers: `@pytest.mark.unit` or `@pytest.mark.integration`
5. Write clear test names: `test_<action>_<scenario>`
