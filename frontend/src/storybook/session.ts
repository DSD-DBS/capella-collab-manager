/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  Session,
  SessionPreparationState,
  SessionState,
} from 'src/app/openapi';
import { mockHttpConnectionMethod, mockToolVersionWithTool } from './tool';
import { mockUser } from './user';

export const mockPersistentSession = createPersistentSessionWithState(
  SessionPreparationState.Completed,
  SessionState.Running,
);

export const mockReadonlySession: Readonly<Session> = {
  ...mockPersistentSession,
  type: 'readonly',
};

export function createPersistentSessionWithState(
  preparationState: SessionPreparationState,
  state: SessionState,
): Session {
  return {
    id: 'vfurvsrldxfwwsqdiqvnufonh',
    created_at: '2024-04-29T15:00:00Z',
    idle_state: {
      available: true,
      terminate_after_minutes: 90,
      idle_for_minutes: 30,
      unavailable_reason: null,
    },
    type: 'persistent',
    version: mockToolVersionWithTool,
    preparation_state: preparationState,
    state: state,
    owner: mockUser,
    connection_method: mockHttpConnectionMethod,
    warnings: [],
    connection_method_id: 'default',
    shared_with: [],
  };
}
