export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  roles: string[];
  role_ids: number[];
  phone?: string | null;
  avatar?: string | null;
}

