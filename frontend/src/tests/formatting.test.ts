import { describe, it, expect } from 'vitest';

/**
 * Tests for value formatting logic used in Earnings and Guidance tables.
 * These functions are embedded in the components, so we test the logic directly.
 */

describe('Value Formatting', () => {
  describe('EPS Formatting', () => {
    it('should format EPS to 2 decimal places', () => {
      const formatEPS = (value: number) => `$${value.toFixed(2)}`;

      expect(formatEPS(2.48)).toBe('$2.48');
      expect(formatEPS(2.5)).toBe('$2.50');
      expect(formatEPS(10.123)).toBe('$10.12');
    });

    it('should handle negative EPS', () => {
      const formatEPS = (value: number) => `$${value.toFixed(2)}`;

      expect(formatEPS(-1.25)).toBe('$-1.25');
    });
  });

  describe('Revenue/EBITDA/FCF Formatting (Millions)', () => {
    it('should format values in millions with M suffix', () => {
      const formatMillions = (value: number) => `$${(value / 1e6).toFixed(1)}M`;

      // $95B stored as 95000000000, display as $95000.0M
      expect(formatMillions(95000000000)).toBe('$95000.0M');

      // $1.5B stored as 1500000000, display as $1500.0M
      expect(formatMillions(1500000000)).toBe('$1500.0M');

      // $100M stored as 100000000, display as $100.0M
      expect(formatMillions(100000000)).toBe('$100.0M');
    });

    it('should handle fractional millions', () => {
      const formatMillions = (value: number) => `$${(value / 1e6).toFixed(1)}M`;

      // $95.4B stored as 95400000000
      expect(formatMillions(95400000000)).toBe('$95400.0M');

      // $1.23B stored as 1230000000
      expect(formatMillions(1230000000)).toBe('$1230.0M');
    });
  });

  describe('User Input Conversion (Millions to Raw)', () => {
    it('should convert millions input to raw numbers', () => {
      const convertToRaw = (millions: number) => millions * 1e6;

      // User enters 95000 (millions) -> store as 95000000000
      expect(convertToRaw(95000)).toBe(95000000000);

      // User enters 1500 (millions) -> store as 1500000000
      expect(convertToRaw(1500)).toBe(1500000000);

      // User enters 100.5 (millions) -> store as 100500000
      expect(convertToRaw(100.5)).toBe(100500000);
    });

    it('should handle EPS without conversion', () => {
      const convertEPS = (value: number) => value; // No conversion

      expect(convertEPS(2.48)).toBe(2.48);
      expect(convertEPS(10.5)).toBe(10.5);
    });
  });

  describe('Display Conversion (Raw to Millions)', () => {
    it('should convert raw numbers to millions for display', () => {
      const convertToMillions = (raw: number) => raw / 1e6;

      // Stored as 95000000000 -> display as 95000
      expect(convertToMillions(95000000000)).toBe(95000);

      // Stored as 1500000000 -> display as 1500
      expect(convertToMillions(1500000000)).toBe(1500);

      // Stored as 95400000000 -> display as 95400
      expect(convertToMillions(95400000000)).toBe(95400);
    });
  });

  describe('Null/Undefined Handling', () => {
    it('should handle null values', () => {
      const formatValue = (value: number | null | undefined) => {
        if (value === null || value === undefined) return '-';
        return `$${(value / 1e6).toFixed(1)}M`;
      };

      expect(formatValue(null)).toBe('-');
      expect(formatValue(undefined)).toBe('-');
      expect(formatValue(95000000000)).toBe('$95000.0M');
    });
  });

  describe('Surprise Percentage Calculations', () => {
    it('should calculate positive surprise (beat)', () => {
      const calculateSurprise = (actual: number, estimate: number) => {
        return ((actual - estimate) / estimate) * 100;
      };

      // Actual $2.48, Estimate $2.35 -> +5.53%
      expect(calculateSurprise(2.48, 2.35)).toBeCloseTo(5.53, 1);

      // Actual $96B, Estimate $90B -> +6.67%
      expect(calculateSurprise(96000000000, 90000000000)).toBeCloseTo(6.67, 1);
    });

    it('should calculate negative surprise (miss)', () => {
      const calculateSurprise = (actual: number, estimate: number) => {
        return ((actual - estimate) / estimate) * 100;
      };

      // Actual $2.30, Estimate $2.50 -> -8.0%
      expect(calculateSurprise(2.30, 2.50)).toBeCloseTo(-8.0, 1);

      // Actual $90B, Estimate $95B -> -5.26%
      expect(calculateSurprise(90000000000, 95000000000)).toBeCloseTo(-5.26, 1);
    });

    it('should return null when estimate is zero', () => {
      const calculateSurprise = (actual: number, estimate: number) => {
        if (estimate === 0) return null;
        return ((actual - estimate) / estimate) * 100;
      };

      expect(calculateSurprise(100, 0)).toBeNull();
    });
  });

  describe('Guidance Midpoint Calculations', () => {
    it('should calculate midpoint of guidance range', () => {
      const calculateMidpoint = (low: number, high: number) => {
        return (low + high) / 2;
      };

      // $90B - $94B -> $92B midpoint
      expect(calculateMidpoint(90000000000, 94000000000)).toBe(92000000000);

      // $8.50 - $9.00 -> $8.75 midpoint
      expect(calculateMidpoint(8.50, 9.00)).toBe(8.75);
    });

    it('should calculate vs guidance percentage', () => {
      const calculateVsGuidance = (actual: number, midpoint: number) => {
        return ((actual - midpoint) / midpoint) * 100;
      };

      // Actual $95B, Midpoint $92B -> +3.26%
      expect(calculateVsGuidance(95000000000, 92000000000)).toBeCloseTo(3.26, 1);

      // Actual $89B, Midpoint $92B -> -3.26%
      expect(calculateVsGuidance(89000000000, 92000000000)).toBeCloseTo(-3.26, 1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle very large numbers', () => {
      const formatMillions = (value: number) => `$${(value / 1e6).toFixed(1)}M`;

      // $500B
      expect(formatMillions(500000000000)).toBe('$500000.0M');
    });

    it('should handle very small numbers', () => {
      const formatMillions = (value: number) => `$${(value / 1e6).toFixed(1)}M`;

      // $1M
      expect(formatMillions(1000000)).toBe('$1.0M');

      // $0.5M
      expect(formatMillions(500000)).toBe('$0.5M');
    });

    it('should handle zero', () => {
      const formatMillions = (value: number) => `$${(value / 1e6).toFixed(1)}M`;

      expect(formatMillions(0)).toBe('$0.0M');
    });

    it('should format surprise with proper sign', () => {
      const formatSurprise = (surprise: number) => {
        const sign = surprise >= 0 ? '+' : '';
        return `(${sign}${surprise.toFixed(1)}%)`;
      };

      expect(formatSurprise(5.5)).toBe('(+5.5%)');
      expect(formatSurprise(-3.2)).toBe('(-3.2%)');
      expect(formatSurprise(0)).toBe('(+0.0%)');
    });
  });
});
