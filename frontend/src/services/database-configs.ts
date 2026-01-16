import { http } from '@/lib/http';
import type {
  DatabaseConfig,
  DatabaseConfigInput,
  DatabaseTestResponse
} from '@/types/database-config';

const baseURL = '';

export const databaseConfigService = {
  /**
   * 获取数据库配置列表
   */
  list: async (params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined)
      queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined)
      queryParams.append('limit', params.limit.toString());
    if (params?.is_active !== undefined)
      queryParams.append('is_active', params.is_active.toString());

    const queryString = queryParams.toString();
    const url = `${baseURL}/backend/database-configs/${
      queryString ? `?${queryString}` : ''
    }`;
    return http.get<DatabaseConfig[]>(url);
  },

  /**
   * 获取单个数据库配置
   */
  get: async (id: number) => {
    return http.get<DatabaseConfig>(
      `${baseURL}/backend/database-configs/${id}/`
    );
  },

  /**
   * 创建数据库配置
   */
  create: async (data: DatabaseConfigInput) => {
    return http.post<DatabaseConfig>(
      `${baseURL}/backend/database-configs/`,
      data
    );
  },

  /**
   * 更新数据库配置
   */
  update: async (id: number, data: Partial<DatabaseConfigInput>) => {
    return http.patch<DatabaseConfig>(
      `${baseURL}/backend/database-configs/${id}/`,
      data
    );
  },

  /**
   * 删除数据库配置
   */
  delete: async (id: number) => {
    return http.delete(`${baseURL}/backend/database-configs/${id}/`);
  },

  /**
   * 测试数据库连接（使用已保存的配置）
   */
  testConnection: async (id: number) => {
    return http.post<DatabaseTestResponse>(
      `${baseURL}/backend/database-configs/${id}/test/`
    );
  },

  /**
   * 测试数据库连接（直接测试，不保存配置）
   */
  testConnectionDirect: async (config: DatabaseConfigInput) => {
    return http.post<DatabaseTestResponse>(
      `${baseURL}/backend/database-configs/test/`,
      config
    );
  },

  /**
   * 查询数据库数据
   */
  queryData: async (
    configId: number,
    params: {
      table_name?: string;
      columns?: string[];
      limit?: number;
      offset?: number;
    }
  ) => {
    return http.post(
      `${baseURL}/backend/database-configs/${configId}/query/`,
      params
    ) as Promise<{
      success: boolean;
      message: string;
      data?: Record<string, unknown>[];
      count?: number;
      error?: string;
    }>;
  }
};
