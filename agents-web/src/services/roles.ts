import { http } from '@/lib/http';
import type { Role, Permission } from '@/types/role';
import type { PaginatedResponse } from '@/types/common';

export const roleService = {
  list: () => http.get<any, PaginatedResponse<Role> | Role[]>('/roles/'),
  create: (data: Partial<Role>) => http.post<any, Role>('/roles/', data),
  update: (id: number, data: Partial<Role>) =>
    http.patch<any, Role>(`/roles/${id}/`, data),
  delete: (id: number) => http.delete(`/roles/${id}/`),
  listPermissions: () =>
    http.get<any, PaginatedResponse<Permission> | Permission[]>('/permissions/')
};
