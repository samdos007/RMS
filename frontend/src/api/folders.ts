import client from './client';
import type { Folder, FolderCreate, FolderListResponse, ThemeOption, ThemeTickerPerformance } from '../types';

export const foldersApi = {
  list: async (search?: string, tags?: string[]): Promise<FolderListResponse> => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (tags?.length) tags.forEach(tag => params.append('tags', tag));

    const response = await client.get('/folders', { params });
    return response.data;
  },

  get: async (id: string): Promise<Folder> => {
    const response = await client.get(`/folders/${id}`);
    return response.data;
  },

  create: async (data: FolderCreate): Promise<Folder> => {
    const response = await client.post('/folders', data);
    return response.data;
  },

  update: async (id: string, data: Partial<FolderCreate>): Promise<Folder> => {
    const response = await client.put(`/folders/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/folders/${id}`);
  },

  // Theme-specific endpoints
  autocompleteThemes: async (search?: string): Promise<ThemeOption[]> => {
    const params = search ? { search } : {};
    const response = await client.get('/folders/themes/autocomplete', { params });
    return response.data;
  },

  addFolderToThemes: async (folderId: string, themeIds: string[]) => {
    const response = await client.post(`/folders/${folderId}/themes`, themeIds);
    return response.data;
  },

  getFoldersInTheme: async (themeId: string): Promise<Folder[]> => {
    const response = await client.get(`/folders/themes/${themeId}/folders`);
    return response.data;
  },

  getThemePerformance: async (folderId: string): Promise<ThemeTickerPerformance[]> => {
    const response = await client.get(`/folders/${folderId}/performance`);
    return response.data;
  },
};
