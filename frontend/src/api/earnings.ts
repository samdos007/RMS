import client from './client';
import type { Earnings, EarningsCreate, EarningsListResponse } from '../types';

export const earningsApi = {
  list: async (folderId: string, ticker?: string): Promise<EarningsListResponse> => {
    const params = new URLSearchParams();
    if (ticker) params.append('ticker', ticker);

    const response = await client.get(`/folders/${folderId}/earnings`, { params });
    return response.data;
  },

  create: async (data: EarningsCreate): Promise<Earnings> => {
    const response = await client.post('/earnings', data);
    return response.data;
  },

  get: async (id: string): Promise<Earnings> => {
    const response = await client.get(`/earnings/${id}`);
    return response.data;
  },

  update: async (id: string, data: Partial<EarningsCreate>): Promise<Earnings> => {
    const response = await client.put(`/earnings/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/earnings/${id}`);
  },

  exportCsv: (folderId: string): string => {
    return `/api/folders/${folderId}/earnings/export`;
  },

  importCsv: async (
    folderId: string,
    file: File
  ): Promise<{ created: number; updated: number; errors: string[]; total_errors: number }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await client.post(`/folders/${folderId}/earnings/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  fetch: async (
    folderId: string,
    ticker: string
  ): Promise<{ ticker: string; created: number; updated: number; message: string }> => {
    const response = await client.post(`/folders/${folderId}/earnings/fetch`, null, {
      params: { ticker },
    });
    return response.data;
  },
};
