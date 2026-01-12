import { http } from '@/lib/http';
import type { Role, Permission } from '@/types/role';

export const roleService = {
  // 统一认证系统的角色管理API
  // nginx配置: location /api/auth/ { proxy_pass http://127.0.0.1:8000/api/v1/; }
  list: () => http.get<Role[]>('/auth/roles'),
  get: (id: number) => http.get<Role>(`/auth/roles/${id}`),
  create: (data: { name: string; description?: string }) =>
    http.post<Role>('/auth/roles', data),
  update: (id: number, data: { name?: string; description?: string }) =>
    http.put<Role>(`/auth/roles/${id}`, data),
  delete: (id: number) => http.delete(`/auth/roles/${id}`),
  listPermissions: () => http.get<Permission[]>('/auth/roles/permissions'),
  assignPermission: (roleId: number, permissionId: number) =>
    http.post(`/auth/roles/${roleId}/permissions/${permissionId}`),
  removePermission: (roleId: number, permissionId: number) =>
    http.delete(`/auth/roles/${roleId}/permissions/${permissionId}`)
};
