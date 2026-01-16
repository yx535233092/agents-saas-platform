import { http } from '@/lib/http';

const baseURL = '';

export interface ChatHistory {
  id: number;
  application_id: number;
  title?: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
  }>;
  user_input?: string;
  created_at: string;
  updated_at: string;
}

export interface ChatHistoryListItem {
  id: number;
  application_id: number;
  title?: string;
  user_input?: string;
  created_at: string;
  updated_at: string;
}

export interface ChatHistoryCreate {
  application_id: number;
  title?: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
  }>;
  user_input?: string;
}

export const chatHistoryService = {
  /**
   * 获取聊天历史记录列表
   */
  list: async (applicationId: number, params?: { skip?: number; limit?: number }) => {
    const queryParams = new URLSearchParams();
    queryParams.append('application_id', applicationId.toString());
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());

    return http.get(
      `${baseURL}/backend/chat-history/?${queryParams.toString()}`
    ) as Promise<ChatHistoryListItem[]>;
  },

  /**
   * 获取单个聊天历史记录
   */
  get: async (id: number) => {
    return http.get(`${baseURL}/backend/chat-history/${id}/`) as Promise<ChatHistory>;
  },

  /**
   * 创建聊天历史记录
   */
  create: async (data: ChatHistoryCreate) => {
    return http.post(`${baseURL}/backend/chat-history/`, data) as Promise<ChatHistory>;
  },

  /**
   * 更新聊天历史记录
   */
  update: async (id: number, data: Partial<ChatHistoryCreate>) => {
    return http.patch(`${baseURL}/backend/chat-history/${id}/`, data) as Promise<ChatHistory>;
  },

  /**
   * 删除聊天历史记录
   */
  delete: async (id: number) => {
    return http.delete(`${baseURL}/backend/chat-history/${id}/`);
  }
};

