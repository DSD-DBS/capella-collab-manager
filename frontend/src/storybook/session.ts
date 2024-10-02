/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Session } from 'src/app/openapi';
import { mockHttpConnectionMethod, mockToolVersionWithTool } from './tool';
import { mockUser } from './user';

export const startedSession = createPersistentSessionWithState('Started');

export function createPersistentSessionWithState(state: string): Session {
  return {
    id: 'vfurvsrldxfwwsqdiqvnufonh',
    created_at: '2024-04-29T15:00:00Z',
    last_seen: '2024-04-29T15:30:00Z',
    type: 'persistent',
    version: mockToolVersionWithTool,
    state: state,
    owner: mockUser,
    connection_method: mockHttpConnectionMethod,
    warnings: [],
    connection_method_id: 'default',
    shared_with: [],
  };
}

export const mockReadonlySession: Readonly<Session> = {
  ...createPersistentSessionWithState('Started'),
  type: 'readonly',
};
