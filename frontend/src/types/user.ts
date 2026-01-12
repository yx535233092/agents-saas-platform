export interface User {
  id: number;
  username: string;
  is_active: boolean;
  role_id: number;
  // 可选字段，用于兼容旧代码
  email?: string;
  first_name?: string;
  last_name?: string;
  roles?: string[];
  role_ids?: number[];
  phone?: string | null;
  avatar?: string | null;
}

