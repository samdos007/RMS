import client from './client';
import type { PriceSnapshot, PriceSnapshotCreate, BackfillResponse } from '../types';

export const pricesApi = {
  list: async (
    ideaId: string,
    startDate?: string,
    endDate?: string,
    limit: number = 100
  ): Promise<PriceSnapshot[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('limit', String(limit));

    const response = await client.get(`/ideas/${ideaId}/prices`, { params });
    return response.data;
  },

  addManual: async (ideaId: string, data: PriceSnapshotCreate): Promise<PriceSnapshot> => {
    const response = await client.post(`/ideas/${ideaId}/prices`, data);
    return response.data;
  },

  fetchLatest: async (ideaId: string): Promise<PriceSnapshot> => {
    const response = await client.post(`/ideas/${ideaId}/prices/fetch`);
    return response.data;
  },

  backfill: async (
    ideaId: string,
    startDate?: string,
    endDate?: string
  ): Promise<BackfillResponse> => {
    const response = await client.post(`/ideas/${ideaId}/prices/backfill`, {
      start_date: startDate,
      end_date: endDate,
    });
    return response.data;
  },

  delete: async (ideaId: string, snapshotId: string): Promise<void> => {
    await client.delete(`/ideas/${ideaId}/prices/${snapshotId}`);
  },
};
