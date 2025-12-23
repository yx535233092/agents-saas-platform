import { http } from '@/lib/http';
import type { User } from '@/types/user';
import type { PaginatedResponse } from '@/types/common';

export const userService = {
  list: () => http.get<any, PaginatedResponse<User> | User[]>('/users/'),
  create: (data: Partial<User>) => http.post<any, User>('/users/', data),
  update: (id: number, data: Partial<User>) =>
    http.patch<any, User>(`/users/${id}/`, data),
  delete: (id: number) => http.delete(`/users/${id}/`)
};
