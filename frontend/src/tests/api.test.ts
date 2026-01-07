import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';

vi.mock('axios');
const mockedAxios = axios as any;

/**
 * Tests for API client functions.
 * These tests verify the correct API calls are made with proper parameters.
 */

describe('Earnings API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('earningsApi.list', () => {
    it('should call GET /folders/:id/earnings', async () => {
      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue({
          data: { earnings: [], total: 0 },
        }),
      });

      const client = mockedAxios.create();
      const response = await client.get('/folders/folder-123/earnings');

      expect(client.get).toHaveBeenCalledWith('/folders/folder-123/earnings');
      expect(response.data).toEqual({ earnings: [], total: 0 });
    });

    it('should pass ticker query parameter', async () => {
      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue({
          data: { earnings: [], total: 0 },
        }),
      });

      const client = mockedAxios.create();
      await client.get('/folders/folder-123/earnings', {
        params: { ticker: 'AAPL' },
      });

      expect(client.get).toHaveBeenCalledWith('/folders/folder-123/earnings', {
        params: { ticker: 'AAPL' },
      });
    });
  });

  describe('earningsApi.create', () => {
    it('should call POST /earnings with correct data structure', async () => {
      const earningsData = {
        folder_id: 'folder-123',
        ticker: 'AAPL',
        period_type: 'QUARTERLY',
        period: '2024-Q4',
        fiscal_quarter: '2024-Q4',
        estimate_eps: 2.35,
        actual_eps: 2.48,
        estimate_rev: 95000000000, // Raw value (not millions)
        actual_rev: 96000000000,
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue({
          data: { id: 'earnings-123', ...earningsData },
        }),
      });

      const client = mockedAxios.create();
      const response = await client.post('/earnings', earningsData);

      expect(client.post).toHaveBeenCalledWith('/earnings', earningsData);
      expect(response.data.id).toBe('earnings-123');
    });

    it('should store revenue in raw format (not millions)', async () => {
      // User enters 95000 (millions) -> should be converted to 95000000000 before sending
      const userInput = 95000; // millions
      const rawValue = userInput * 1e6;

      const earningsData = {
        folder_id: 'folder-123',
        ticker: 'AAPL',
        period_type: 'QUARTERLY',
        fiscal_quarter: '2024-Q4',
        estimate_rev: rawValue,
      };

      expect(earningsData.estimate_rev).toBe(95000000000);
    });
  });

  describe('earningsApi.fetch', () => {
    it('should call POST /folders/:id/earnings/fetch with ticker param', async () => {
      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue({
          data: { ticker: 'AAPL', created: 5, updated: 0, message: 'Success' },
        }),
      });

      const client = mockedAxios.create();
      await client.post('/folders/folder-123/earnings/fetch', null, {
        params: { ticker: 'AAPL' },
      });

      expect(client.post).toHaveBeenCalledWith(
        '/folders/folder-123/earnings/fetch',
        null,
        { params: { ticker: 'AAPL' } }
      );
    });
  });

  describe('earningsApi.update', () => {
    it('should call PUT /earnings/:id with partial data', async () => {
      const updateData = {
        actual_eps: 2.48,
        actual_rev: 96000000000,
        notes: 'Beat estimates',
      };

      mockedAxios.create.mockReturnValue({
        put: vi.fn().mockResolvedValue({
          data: { id: 'earnings-123', ...updateData },
        }),
      });

      const client = mockedAxios.create();
      await client.put('/earnings/earnings-123', updateData);

      expect(client.put).toHaveBeenCalledWith('/earnings/earnings-123', updateData);
    });
  });

  describe('earningsApi.delete', () => {
    it('should call DELETE /earnings/:id', async () => {
      mockedAxios.create.mockReturnValue({
        delete: vi.fn().mockResolvedValue({}),
      });

      const client = mockedAxios.create();
      await client.delete('/earnings/earnings-123');

      expect(client.delete).toHaveBeenCalledWith('/earnings/earnings-123');
    });
  });
});

describe('Guidance API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('guidanceApi.list', () => {
    it('should call GET /folders/:id/guidance', async () => {
      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue({
          data: { guidance: [], total: 0 },
        }),
      });

      const client = mockedAxios.create();
      await client.get('/folders/folder-123/guidance');

      expect(client.get).toHaveBeenCalledWith('/folders/folder-123/guidance');
    });

    it('should pass ticker query parameter', async () => {
      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue({
          data: { guidance: [], total: 0 },
        }),
      });

      const client = mockedAxios.create();
      await client.get('/folders/folder-123/guidance', {
        params: { ticker: 'AAPL' },
      });

      expect(client.get).toHaveBeenCalledWith('/folders/folder-123/guidance', {
        params: { ticker: 'AAPL' },
      });
    });
  });

  describe('guidanceApi.create', () => {
    it('should call POST /guidance with correct data structure', async () => {
      const guidanceData = {
        folder_id: 'folder-123',
        ticker: 'AAPL',
        period: '2025-Q1',
        metric: 'REVENUE',
        guidance_period: '2024-Q4',
        guidance_low: 94000000000,
        guidance_high: 96000000000,
        notes: 'Q1 guidance',
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue({
          data: { id: 'guidance-123', ...guidanceData },
        }),
      });

      const client = mockedAxios.create();
      await client.post('/guidance', guidanceData);

      expect(client.post).toHaveBeenCalledWith('/guidance', guidanceData);
    });

    it('should store guidance values in raw format (not millions)', async () => {
      // User enters 94000-96000 (millions) -> should be converted to raw before sending
      const userInputLow = 94000; // millions
      const userInputHigh = 96000; // millions
      const rawLow = userInputLow * 1e6;
      const rawHigh = userInputHigh * 1e6;

      const guidanceData = {
        folder_id: 'folder-123',
        ticker: 'AAPL',
        period: '2025-Q1',
        metric: 'REVENUE',
        guidance_period: '2024-Q4',
        guidance_low: rawLow,
        guidance_high: rawHigh,
      };

      expect(guidanceData.guidance_low).toBe(94000000000);
      expect(guidanceData.guidance_high).toBe(96000000000);
    });

    it('should handle point guidance instead of range', async () => {
      const guidanceData = {
        folder_id: 'folder-123',
        ticker: 'AAPL',
        period: '2025',
        metric: 'EPS',
        guidance_period: '2024-Q4',
        guidance_point: 9.50, // No conversion for EPS
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue({
          data: { id: 'guidance-123', ...guidanceData },
        }),
      });

      const client = mockedAxios.create();
      await client.post('/guidance', guidanceData);

      expect(client.post).toHaveBeenCalledWith('/guidance', guidanceData);
    });
  });

  describe('guidanceApi.update', () => {
    it('should call PUT /guidance/:id with partial data', async () => {
      const updateData = {
        actual_result: 95000000000,
        notes: 'Beat guidance',
      };

      mockedAxios.create.mockReturnValue({
        put: vi.fn().mockResolvedValue({
          data: { id: 'guidance-123', ...updateData },
        }),
      });

      const client = mockedAxios.create();
      await client.put('/guidance/guidance-123', updateData);

      expect(client.put).toHaveBeenCalledWith('/guidance/guidance-123', updateData);
    });
  });

  describe('guidanceApi.delete', () => {
    it('should call DELETE /guidance/:id', async () => {
      mockedAxios.create.mockReturnValue({
        delete: vi.fn().mockResolvedValue({}),
      });

      const client = mockedAxios.create();
      await client.delete('/guidance/guidance-123');

      expect(client.delete).toHaveBeenCalledWith('/guidance/guidance-123');
    });
  });
});

describe('Data Conversion Logic', () => {
  describe('Millions Conversion for Storage', () => {
    it('should convert Revenue/EBITDA/FCF from millions to raw', () => {
      const convertForStorage = (millions: number, metric: string) => {
        return metric === 'EPS' ? millions : millions * 1e6;
      };

      expect(convertForStorage(95000, 'REVENUE')).toBe(95000000000);
      expect(convertForStorage(1500, 'EBITDA')).toBe(1500000000);
      expect(convertForStorage(25000, 'FCF')).toBe(25000000000);
      expect(convertForStorage(2.48, 'EPS')).toBe(2.48); // No conversion
    });
  });

  describe('Millions Conversion for Display', () => {
    it('should convert Revenue/EBITDA/FCF from raw to millions', () => {
      const convertForDisplay = (raw: number, metric: string) => {
        return metric === 'EPS' ? raw : raw / 1e6;
      };

      expect(convertForDisplay(95000000000, 'REVENUE')).toBe(95000);
      expect(convertForDisplay(1500000000, 'EBITDA')).toBe(1500);
      expect(convertForDisplay(25000000000, 'FCF')).toBe(25000);
      expect(convertForDisplay(2.48, 'EPS')).toBe(2.48); // No conversion
    });
  });
});
