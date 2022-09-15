/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

export interface Session {
  ports: Array<string>;
  created_at: string;
  id: string;
  last_seen: string;
  type: 'persistent' | 'readonly';
  rdp_username: string;
  rdp_password: string;
  guacamole_username: string;
  guacamole_password: string;
  guacamole_connection_id: string;
  repository: string;
  state: string;
  owner: string;
  download_in_progress: boolean;
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

export interface SessionUsage {
  free: number;
  total: number;
  errors: Array<string>;
}

export interface PathNode {
  path: string;
  name: string;
  type: 'file' | 'directory';
  isNew: boolean;
  children: PathNode[] | null;
}
