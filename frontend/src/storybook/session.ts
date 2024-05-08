/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  ReadonlySession,
  Session,
} from 'src/app/sessions/service/session.service';
import { mockHttpConnectionMethod, mockToolVersionWithTool } from './tool';
import { mockUser } from './user';

export const startedSession = createPersistentSessionWithState('Started');

export function createPersistentSessionWithState(state: string): Session {
  return {
    id: '1',
    created_at: '2024-04-29T15:00:00Z',
    last_seen: '2024-04-29T15:30:00Z',
    type: 'persistent',
    project: undefined,
    version: mockToolVersionWithTool,
    state: state,
    owner: mockUser,
    download_in_progress: false,
    connection_method: mockHttpConnectionMethod,
  };
}

export const mockSuccessReadonlySession: Readonly<ReadonlySession> = {
  id: '1',
  created_at: '2024-04-29T15:00:00Z',
  last_seen: '2024-04-29T15:30:00Z',
  type: 'readonly' as const,
  project: {
    name: 'fake-name',
    slug: 'fake-slug',
    description: 'fake-description',
    visibility: 'private' as const,
    type: 'general' as const,
    users: { leads: 1, contributors: 0, subscribers: 0 },
    is_archived: false,
  },
  version: mockToolVersionWithTool,
  state: 'Started',
  owner: mockUser,
  download_in_progress: false,
  connection_method: mockHttpConnectionMethod,
};
