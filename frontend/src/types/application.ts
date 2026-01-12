// 应用管理类型定义

export interface Application {
  id: number;
  name: string;
  description?: string;
  app_type: 'secret_judgement' | 'custom'; // 应用类型：涉密研判、自定义
  api_endpoint: string; // API 端点地址
  api_method: 'POST' | 'GET' | 'PUT' | 'DELETE'; // HTTP 方法
  request_format?: 'json' | 'form-data' | 'x-www-form-urlencoded'; // 请求格式
  response_format?: 'json' | 'sse' | 'stream'; // 响应格式
  headers?: Record<string, string>; // 自定义请求头
  timeout?: number; // 超时时间（秒）
  icon?: string; // 图标标识
  icon_color?: string; // 图标颜色
  is_active: boolean; // 是否启用
  sort_order: number; // 排序
  created_at: string;
  updated_at: string;
}

// 创建/更新应用的请求体
export interface ApplicationInput {
  name: string;
  description?: string;
  app_type: 'secret_judgement' | 'custom';
  api_endpoint: string;
  api_method?: 'POST' | 'GET' | 'PUT' | 'DELETE';
  request_format?: 'json' | 'form-data' | 'x-www-form-urlencoded';
  response_format?: 'json' | 'sse' | 'stream';
  headers?: Record<string, string>;
  timeout?: number;
  icon?: string;
  icon_color?: string;
  is_active?: boolean;
  sort_order?: number;
}

// 应用类型选项
export const APP_TYPE_OPTIONS = [
  { value: 'secret_judgement', label: '涉密研判智能体' },
  { value: 'custom', label: '自定义应用' }
];

// HTTP 方法选项
export const HTTP_METHOD_OPTIONS = [
  { value: 'POST', label: 'POST' },
  { value: 'GET', label: 'GET' },
  { value: 'PUT', label: 'PUT' },
  { value: 'DELETE', label: 'DELETE' }
];

// 请求格式选项
export const REQUEST_FORMAT_OPTIONS = [
  { value: 'json', label: 'JSON' },
  { value: 'form-data', label: 'Form Data' },
  { value: 'x-www-form-urlencoded', label: 'URL Encoded' }
];

// 响应格式选项
export const RESPONSE_FORMAT_OPTIONS = [
  { value: 'json', label: 'JSON' },
  { value: 'sse', label: 'Server-Sent Events (SSE)' },
  { value: 'stream', label: 'Stream' }
];

// 图标选项
export const APP_ICON_OPTIONS = [
  { value: 'shield', label: 'Shield 🛡️' },
  { value: 'lock', label: 'Lock 🔒' },
  { value: 'search', label: 'Search 🔍' },
  { value: 'bot', label: 'Bot 🤖' },
  { value: 'sparkles', label: 'Sparkles ✨' }
];

// 图标颜色选项
export const APP_ICON_COLOR_OPTIONS = [
  { value: 'text-blue-500', label: '蓝色' },
  { value: 'text-emerald-500', label: '绿色' },
  { value: 'text-violet-500', label: '紫色' },
  { value: 'text-orange-500', label: '橙色' },
  { value: 'text-amber-500', label: '琥珀色' },
  { value: 'text-cyan-500', label: '青色' },
  { value: 'text-purple-500', label: '深紫色' },
  { value: 'text-rose-500', label: '玫红色' }
];

