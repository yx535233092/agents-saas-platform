import { http } from '@/lib/http';
import type { Application, ApplicationInput } from '@/types/application';

// 分页响应类型
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 获取应用列表（管理员接口）
export async function getApplications(): Promise<Application[]> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const response: any = await http.get('/backend/applications/');
  // 处理分页响应
  if (response && typeof response === 'object' && 'results' in response) {
    return (response as PaginatedResponse<Application>).results;
  }
  return response as Application[];
}

// 获取单个应用
export async function getApplication(id: number): Promise<Application> {
  return http.get(`/backend/applications/${id}/`) as Promise<Application>;
}

// 创建应用
export async function createApplication(
  data: ApplicationInput
): Promise<Application> {
  return http.post('/backend/applications/', data) as Promise<Application>;
}

// 更新应用
export async function updateApplication(
  id: number,
  data: Partial<ApplicationInput>
): Promise<Application> {
  return http.patch(
    `/backend/applications/${id}/`,
    data
  ) as Promise<Application>;
}

// 删除应用
export async function deleteApplication(id: number): Promise<void> {
  return http.delete(`/backend/applications/${id}/`) as Promise<void>;
}

// 测试应用连接
export async function testApplication(
  id: number,
  testData?: Record<string, unknown>
): Promise<{ success: boolean; message: string; data?: unknown }> {
  return http.post(
    `/backend/applications/${id}/test/`,
    testData || {}
  ) as Promise<{
    success: boolean;
    message: string;
    data?: unknown;
  }>;
}

// 获取公开的应用列表（用于前台应用广场，无需认证）
export async function getPublicApplications(): Promise<Application[]> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const response: any = await http.get('/backend/applications/public/');
  // 处理分页响应
  if (response && typeof response === 'object' && 'results' in response) {
    return (response as PaginatedResponse<Application>).results;
  }
  return response as Application[];
}
