/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

export interface Session {
  ports: string[];
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
  t4c_password: string;
}

export interface User {
  id: number;
  name: string;
  role: 'user' | 'administrator';
}

export type Warnings = 'LICENCE_LIMIT' | 'NO_GIT_MODEL_DEFINED';

export interface ProjectUser {
  project_name: string;
  permission: 'read' | 'write';
  role: 'user' | 'manager' | 'administrator';
  warnings: Array<Warnings>;
  user: User;
}

export interface SessionUsage {
  free: number;
  total: number;
}

export interface PathNode {
  path: string;
  name: string;
  type: 'file' | 'directory';
  isNew: boolean;
  children: PathNode[] | null;
}
