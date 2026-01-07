import client from './client';
import type { Note, NoteCreate, NoteType } from '../types';

export const notesApi = {
  listForIdea: async (ideaId: string, noteType?: NoteType): Promise<Note[]> => {
    const params = new URLSearchParams();
    if (noteType) params.append('note_type', noteType);

    const response = await client.get(`/ideas/${ideaId}/notes`, { params });
    return response.data;
  },

  listForFolder: async (folderId: string, noteType?: NoteType): Promise<Note[]> => {
    const params = new URLSearchParams();
    if (noteType) params.append('note_type', noteType);

    const response = await client.get(`/folders/${folderId}/notes`, { params });
    return response.data;
  },

  create: async (data: NoteCreate): Promise<Note> => {
    const response = await client.post('/notes', data);
    return response.data;
  },

  get: async (id: string): Promise<Note> => {
    const response = await client.get(`/notes/${id}`);
    return response.data;
  },

  update: async (id: string, data: Partial<NoteCreate>): Promise<Note> => {
    const response = await client.put(`/notes/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/notes/${id}`);
  },

  search: async (
    query: string,
    folderId?: string,
    noteType?: NoteType,
    limit: number = 50
  ): Promise<Note[]> => {
    const params = new URLSearchParams();
    params.append('q', query);
    if (folderId) params.append('folder_id', folderId);
    if (noteType) params.append('note_type', noteType);
    params.append('limit', String(limit));

    const response = await client.get('/search/notes', { params });
    return response.data;
  },
};
