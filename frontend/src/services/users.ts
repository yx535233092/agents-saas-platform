import { http } from '@/lib/http';
import type { User } from '@/types/user';

export const userService = {
  // 统一认证系统的用户管理API
  // nginx配置: location /api/auth/ { proxy_pass http://127.0.0.1:8000/api/v1/; }
  list: () => http.get<User[]>('/auth/users'),
  create: (data: { username: string; password: string; role_id?: number }) =>
    http.post<User>('/auth/auth/register', data),
  update: (id: number, data: { username?: string; password?: string; is_active?: boolean; role_id?: number }) =>
    http.put<User>(`/auth/users/${id}`, data),
  updateRole: (id: number, role_id: number) =>
    http.put(`/auth/users/${id}/role?role_id=${role_id}`),
  delete: (id: number) => http.delete(`/auth/users/${id}`),
  get: (id: number) => http.get<User>(`/auth/users/${id}`)
};
