import client from './client';
import type { Guidance, GuidanceCreate, GuidanceListResponse } from '../types';

export const guidanceApi = {
  /**
   * List guidance records for a folder
   */
  async list(folderId: string, ticker?: string): Promise<GuidanceListResponse> {
    const params = ticker ? { ticker } : {};
    const response = await client.get(`/folders/${folderId}/guidance`, { params });
    return response.data;
  },

  /**
   * Get a single guidance record by ID
   */
  async get(guidanceId: string): Promise<Guidance> {
    const response = await client.get(`/guidance/${guidanceId}`);
    return response.data;
  },

  /**
   * Create a new guidance record
   */
  async create(data: GuidanceCreate): Promise<Guidance> {
    const response = await client.post('/guidance', data);
    return response.data;
  },

  /**
   * Update an existing guidance record
   */
  async update(guidanceId: string, data: Partial<GuidanceCreate>): Promise<Guidance> {
    const response = await client.put(`/guidance/${guidanceId}`, data);
    return response.data;
  },

  /**
   * Delete a guidance record
   */
  async delete(guidanceId: string): Promise<void> {
    await client.delete(`/guidance/${guidanceId}`);
  },
};
