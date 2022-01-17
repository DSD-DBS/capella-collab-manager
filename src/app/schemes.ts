export interface Session {
  ports: Array<string>;
  created_at: string;
  id: string;
  type: 'persistent' | 'readonly';
  rdp_username: string;
  rdp_password: string;
  guacamole_username: string;
  guacamole_password: string;
  guacamole_connection_id: string;
  repository: string;
  state: string;
  owner: string;
  mac: string;
}

export interface User {
  id: number;
  name: string;
  role: 'user' | 'administrator';
}

export interface RepositoryUser {
  repository_name: string;
  username: string;
  permission: 'read' | 'write';
  role: 'user' | 'manager' | 'administrator';
}

export interface SessionsUsage {
  free: number;
  total: number;
}
