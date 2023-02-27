/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { User } from 'src/app/services/user/user.service';
import { ToolVersionWithTool } from 'src/app/settings/core/tools-settings/tool.service';
import { Project } from './projects/service/project.service';

export interface Session {
  created_at: string;
  id: string;
  last_seen: string;
  type: 'persistent' | 'readonly';
  rdp_password: string;
  guacamole_username: string;
  guacamole_password: string;
  guacamole_connection_id: string;
  jupyter_uri: string | undefined;
  project: Project | undefined;
  version: ToolVersionWithTool | undefined;
  state: string;
  owner: User;
  t4c_password: string;
  download_in_progress: boolean;
}

export interface PathNode {
  path: string;
  name: string;
  type: 'file' | 'directory';
  isNew: boolean;
  children: PathNode[] | null;
}
