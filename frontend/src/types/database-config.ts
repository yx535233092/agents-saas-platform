export interface DatabaseConfig {
  id: number;
  name: string;
  description?: string;
  db_type: 'sqlite' | 'postgresql' | 'mysql' | 'mssql';
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  connection_string?: string;
  extra_params?: Record<string, unknown>;
  is_active: boolean;
  is_default: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface DatabaseConfigInput {
  name: string;
  description?: string;
  db_type: 'sqlite' | 'postgresql' | 'mysql' | 'mssql';
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  connection_string?: string;
  extra_params?: Record<string, unknown>;
  is_active?: boolean;
  is_default?: boolean;
  sort_order?: number;
}

export interface DatabaseTestResponse {
  success: boolean;
  message: string;
  details?: Record<string, unknown>;
}

export const DB_TYPE_OPTIONS = [
  { value: 'sqlite', label: 'SQLite' },
  { value: 'postgresql', label: 'PostgreSQL' },
  { value: 'mysql', label: 'MySQL' },
  { value: 'mssql', label: 'MSSQL (SQL Server)' }
] as const;

