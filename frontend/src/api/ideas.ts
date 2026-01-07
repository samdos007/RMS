import client from './client';
import type {
  Idea,
  IdeaCreate,
  IdeaListResponse,
  IdeaStatus,
  CloseIdeaRequest,
  PnLResponse,
  PnLHistoryResponse,
} from '../types';

export const ideasApi = {
  list: async (
    folderId?: string,
    status?: IdeaStatus[],
    includePnl: boolean = false
  ): Promise<IdeaListResponse> => {
    const params = new URLSearchParams();
    if (folderId) params.append('folder_id', folderId);
    if (status?.length) status.forEach(s => params.append('status', s));
    params.append('include_pnl', String(includePnl));

    const response = await client.get('/ideas', { params });
    return response.data;
  },

  get: async (id: string, includePnl: boolean = true): Promise<Idea> => {
    const response = await client.get(`/ideas/${id}`, {
      params: { include_pnl: includePnl },
    });
    return response.data;
  },

  create: async (data: IdeaCreate): Promise<Idea> => {
    const response = await client.post('/ideas', data);
    return response.data;
  },

  update: async (id: string, data: Partial<IdeaCreate>): Promise<Idea> => {
    const response = await client.put(`/ideas/${id}`, data);
    return response.data;
  },

  updateStatus: async (id: string, status: IdeaStatus): Promise<Idea> => {
    const response = await client.patch(`/ideas/${id}/status`, { status });
    return response.data;
  },

  close: async (id: string, data: CloseIdeaRequest): Promise<Idea> => {
    const response = await client.post(`/ideas/${id}/close`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/ideas/${id}`);
  },

  getPnl: async (id: string): Promise<PnLResponse> => {
    const response = await client.get(`/ideas/${id}/pnl`);
    return response.data;
  },

  getPnlHistory: async (id: string): Promise<PnLHistoryResponse> => {
    const response = await client.get(`/ideas/${id}/pnl/history`);
    return response.data;
  },
};
