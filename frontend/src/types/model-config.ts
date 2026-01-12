// 模型配置类型定义

export interface ModelConfig {
  id: number;
  name: string;
  model_id: string;
  description: string;
  provider: string;
  icon: 'sparkles' | 'zap' | 'brain' | 'cpu' | 'bot';
  icon_color: string;
  max_tokens: number;
  api_base_url?: string;
  api_key?: string;
  api_key_env?: string;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

// 公开接口返回的模型配置（不包含敏感信息）
export interface ModelConfigPublic {
  id: number;
  name: string;
  model_id: string;
  description: string;
  provider: string;
  icon: 'sparkles' | 'zap' | 'brain' | 'cpu' | 'bot';
  icon_color: string;
  max_tokens: number;
}

// 创建/更新模型配置的请求体
export interface ModelConfigInput {
  name: string;
  model_id: string;
  description?: string;
  provider: string;
  icon?: string;
  icon_color?: string;
  max_tokens?: number;
  api_base_url?: string;
  api_key?: string;
  api_key_env?: string;
  is_active?: boolean;
  sort_order?: number;
}

// Provider 选项
export const PROVIDER_OPTIONS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'alibaba', label: 'Alibaba' },
  { value: 'siliconflow', label: 'SiliconFlow' },
  { value: 'other', label: 'Other' }
];

// Icon 选项
export const ICON_OPTIONS = [
  { value: 'sparkles', label: 'Sparkles ✨' },
  { value: 'zap', label: 'Zap ⚡' },
  { value: 'brain', label: 'Brain 🧠' },
  { value: 'cpu', label: 'CPU 💻' },
  { value: 'bot', label: 'Bot 🤖' }
];

// 图标颜色选项
export const ICON_COLOR_OPTIONS = [
  { value: 'text-blue-500', label: '蓝色' },
  { value: 'text-emerald-500', label: '绿色' },
  { value: 'text-violet-500', label: '紫色' },
  { value: 'text-orange-500', label: '橙色' },
  { value: 'text-amber-500', label: '琥珀色' },
  { value: 'text-cyan-500', label: '青色' },
  { value: 'text-purple-500', label: '深紫色' },
  { value: 'text-rose-500', label: '玫红色' }
];
