import client from './client';
import type { Attachment } from '../types';

export const attachmentsApi = {
  listForFolder: async (folderId: string): Promise<Attachment[]> => {
    const response = await client.get(`/folders/${folderId}/attachments`);
    return response.data;
  },

  listForIdea: async (ideaId: string): Promise<Attachment[]> => {
    const response = await client.get(`/ideas/${ideaId}/attachments`);
    return response.data;
  },

  uploadToFolder: async (folderId: string, file: File): Promise<Attachment> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await client.post(`/folders/${folderId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadToIdea: async (ideaId: string, file: File): Promise<Attachment> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await client.post(`/ideas/${ideaId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  get: async (id: string): Promise<Attachment> => {
    const response = await client.get(`/attachments/${id}`);
    return response.data;
  },

  download: (id: string): string => {
    return `/api/attachments/${id}/download`;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/attachments/${id}`);
  },
};
