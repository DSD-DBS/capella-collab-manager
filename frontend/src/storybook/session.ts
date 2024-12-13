/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  ProjectType,
  Session,
  SessionPreparationState,
  SessionState,
  SessionType,
} from 'src/app/openapi';
import { mockProject } from 'src/storybook/project';
import {
  mockHttpConnectionMethod,
  mockToolVersionWithTool,
  mockTrainingControllerVersionWithTool,
} from './tool';
import { mockUser } from './user';

export const mockPersistentSession: Readonly<Session> = {
  id: 'vfurvsrldxfwwsqdiqvnufonh',
  created_at: '2024-04-29T15:00:00Z',
  idle_state: {
    available: true,
    terminate_after_minutes: 90,
    idle_for_minutes: 30,
    unavailable_reason: null,
  },
  type: SessionType.Persistent,
  version: mockToolVersionWithTool,
  preparation_state: SessionPreparationState.Completed,
  state: SessionState.Running,
  owner: mockUser,
  connection_method: { ...mockHttpConnectionMethod, name: 'Xpra' },
  internal_endpoint:
    'vfurvsrldxfwwsqdiqvnufonh.collab-sessions.svc.cluster.local',
  warnings: [],
  connection_method_id: 'default',
  shared_with: [],
  project: null,
};

export const mockReadonlySession: Readonly<Session> = {
  ...mockPersistentSession,
  type: SessionType.Readonly,
};

export const mockTrainingSession: Readonly<Session> = {
  ...mockPersistentSession,
  project: {
    ...mockProject,
    type: ProjectType.Training,
    name: 'PVMT Training',
  },
  version: mockTrainingControllerVersionWithTool,
  connection_method: mockHttpConnectionMethod,
};
