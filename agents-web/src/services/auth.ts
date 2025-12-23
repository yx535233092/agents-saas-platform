import { http } from '@/lib/http';
import type { LoginResponse } from '@/types/auth';

export const authService = {
  login: (data: any) => http.post<any, LoginResponse>('/auth/login/', data),

  register: (data: any) => http.post('/users/', data),

  me: () => http.get('/auth/me/'),

  refreshToken: (refresh: string) => http.post('/auth/refresh/', { refresh })
};
