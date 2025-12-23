import { http } from '@/lib/http';
import type {
  ModelConfig,
  ModelConfigPublic,
  ModelConfigInput
} from '@/types/model-config';

// 分页响应类型
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 获取模型配置列表（管理员接口）
export async function getModelConfigs(): Promise<ModelConfig[]> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const response: any = await http.get('/model-configs/');
  // 处理分页响应
  if (response && typeof response === 'object' && 'results' in response) {
    return (response as PaginatedResponse<ModelConfig>).results;
  }
  return response as ModelConfig[];
}

// 获取单个模型配置
export async function getModelConfig(id: number): Promise<ModelConfig> {
  return http.get(`/model-configs/${id}/`) as Promise<ModelConfig>;
}

// 创建模型配置
export async function createModelConfig(
  data: ModelConfigInput
): Promise<ModelConfig> {
  return http.post('/model-configs/', data) as Promise<ModelConfig>;
}

// 更新模型配置
export async function updateModelConfig(
  id: number,
  data: Partial<ModelConfigInput>
): Promise<ModelConfig> {
  return http.patch(`/model-configs/${id}/`, data) as Promise<ModelConfig>;
}

// 删除模型配置
export async function deleteModelConfig(id: number): Promise<void> {
  return http.delete(`/model-configs/${id}/`) as Promise<void>;
}

// 获取公开的模型列表（用于对话广场，无需认证）
export async function getPublicModelConfigs(): Promise<ModelConfigPublic[]> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const response: any = await http.get('/model-configs/public/');
  // 处理分页响应
  if (response && typeof response === 'object' && 'results' in response) {
    return (response as PaginatedResponse<ModelConfigPublic>).results;
  }
  return response as ModelConfigPublic[];
}
