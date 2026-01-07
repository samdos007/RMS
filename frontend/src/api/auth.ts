import client from './client';
import type { AuthStatus, User } from '../types';

export const authApi = {
  getStatus: async (): Promise<AuthStatus> => {
    const response = await client.get('/auth/status');
    return response.data;
  },

  setup: async (username: string, password: string): Promise<{ message: string; username: string }> => {
    const response = await client.post('/auth/setup', { username, password });
    return response.data;
  },

  login: async (username: string, password: string): Promise<{ message: string; username: string }> => {
    const response = await client.post('/auth/login', { username, password });
    return response.data;
  },

  logout: async (): Promise<void> => {
    await client.post('/auth/logout');
  },

  getMe: async (): Promise<User> => {
    const response = await client.get('/auth/me');
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await client.post('/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};
