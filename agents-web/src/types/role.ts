export interface Permission {
  id: number;
  name: string;
  codename: string;
  content_type: number;
}

export interface Role {
  id: number;
  name: string;
  permissions: Permission[];
  permission_ids: number[];
}
