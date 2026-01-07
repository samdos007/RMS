# Frontend Tests

Comprehensive test suite for the RMS frontend application.

## Setup

First, install dependencies:

```bash
cd frontend
npm install
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode (recommended during development)
npm test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test formatting.test.ts

# Run tests matching a pattern
npm test -- --grep "EPS"
```

## Test Organization

### formatting.test.ts
Tests for value formatting and conversion logic:
- **EPS Formatting**: $X.XX format
- **Revenue/EBITDA/FCF Formatting**: $X.XM format (millions)
- **User Input Conversion**: Millions to raw numbers (multiply by 1e6)
- **Display Conversion**: Raw numbers to millions (divide by 1e6)
- **Null/Undefined Handling**: Display "-" for missing values
- **Surprise Percentage Calculations**: Beat/miss calculations
- **Guidance Midpoint Calculations**: Range midpoint and vs-guidance percentage
- **Edge Cases**: Very large/small numbers, zero, sign formatting

### api.test.ts
Tests for API client functions:
- **Earnings API**: list, create, update, delete, fetch
- **Guidance API**: list, create, update, delete
- **Data Conversion**: Millions ↔ raw conversion for storage and display

## Key Testing Concepts

### Value Conversion (Critical!)

The app uses **millions** as the display unit for Revenue, EBITDA, and FCF, but stores **raw values** in the database:

**For Display:**
- Raw value: `95000000000` (stored in DB)
- Display value: `95000` millions
- Formatted: `$95000.0M`

**For Storage:**
- User enters: `95000` (millions)
- Convert: `95000 * 1e6 = 95000000000`
- Store: `95000000000` (raw)

**EPS is NOT converted** (already in dollars):
- User enters: `2.48`
- Store: `2.48`
- Display: `$2.48`

### Surprise Calculations

```typescript
surprise_pct = ((actual - estimate) / estimate) * 100

// Example:
// Actual: $2.48, Estimate: $2.35
// (2.48 - 2.35) / 2.35 * 100 = 5.53%
```

### Guidance Calculations

```typescript
midpoint = (guidance_low + guidance_high) / 2
vs_guidance_pct = ((actual - midpoint) / midpoint) * 100

// Example:
// Guidance: $90B - $94B, Actual: $95B
// Midpoint: $92B
// (95 - 92) / 92 * 100 = 3.26%
```

## Test Coverage Goals

- ✅ Value formatting logic: 100%
- ✅ API client calls: 100%
- ✅ Conversion functions: 100%

## Adding New Tests

1. Create test file: `<feature>.test.ts` or `<feature>.test.tsx`
2. Import test utilities:
   ```typescript
   import { describe, it, expect } from 'vitest';
   ```
3. For component tests, use custom render:
   ```typescript
   import { render, screen } from '../tests/test-utils';
   ```
4. Write descriptive test names
5. Test both happy paths and edge cases

## CI/CD Integration

Tests run automatically on:
- Pre-commit (if configured)
- Pull requests
- Main branch pushes

## Debugging Tests

```bash
# Run tests with detailed output
npm test -- --reporter=verbose

# Run single test in debug mode
npm test -- --inspect-brk formatting.test.ts
```

## Common Issues

### Mock Issues
If mocks aren't working, ensure they're defined before imports:
```typescript
vi.mock('axios');
import { earningsApi } from '../api/earnings';
```

### Async Issues
Always `await` async operations in tests:
```typescript
const result = await someAsyncFunction();
expect(result).toBe(expected);
```

### Component Test Failures
Ensure all providers are included in test-utils.tsx:
- QueryClientProvider
- BrowserRouter
- ToastProvider

## Future Test Additions

When adding new features, add tests for:
- [ ] EarningsTable component rendering
- [ ] GuidanceTable component rendering
- [ ] Form validation logic
- [ ] User interactions (button clicks, form submissions)
- [ ] Error handling
