/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { Observable, of } from 'rxjs';
import { User } from 'src/app/services/user/user.service';
import {
  ConnectionMethod,
  Tool,
  ToolVersionWithTool,
} from 'src/app/settings/core/tools-settings/tool.service';
import { Session } from '../../service/session.service';
import { UserSessionService } from '../../service/user-session.service';
import { ActiveSessionsComponent } from './active-sessions.component';

class MockUserSessionService implements Partial<UserSessionService> {
  public readonly sessions$: Observable<Session[] | undefined> = of(undefined);

  constructor(session?: Session, empty?: boolean) {
    if (session !== undefined) {
      this.sessions$ = of([session]);
    } else if (empty === true) {
      this.sessions$ = of([]);
    }
  }
}

const meta: Meta<ActiveSessionsComponent> = {
  title: 'Session Components / Active Sessions',
  component: ActiveSessionsComponent,
};

export default meta;
type Story = StoryObj<ActiveSessionsComponent>;

const connectionMethod: ConnectionMethod = {
  id: '1',
  name: 'fakeConnectionMethod',
  type: 'http',
};

const user: User = {
  id: 1,
  name: 'fakeUser',
  role: 'user',
  created: '2024-04-29T14:00:00Z',
  last_login: '2024-04-29T14:59:00Z',
};

const tool: Tool = {
  id: 1,
  name: 'fakeTool',
  integrations: {
    t4c: true,
    pure_variants: false,
    jupyter: false,
  },
  config: {
    connection: {
      methods: [connectionMethod],
    },
    provisioning: {},
    persistent_workspaces: { mounting_enabled: true },
  },
};

const versionWithTool: ToolVersionWithTool = {
  id: 1,
  name: 'fakeVersion',
  config: {
    is_recommended: false,
    is_deprecated: false,
    compatible_versions: [],
  },
  tool: tool,
};

function createPersistentSessionWithState(state: string): Session {
  return {
    id: '1',
    created_at: '2024-04-29T15:00:00Z',
    last_seen: '2024-04-29T15:30:00Z',
    type: 'persistent',
    project: undefined,
    version: versionWithTool,
    state: state,
    owner: user,
    download_in_progress: false,
    connection_method: connectionMethod,
  };
}

const successReadonlySession = {
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
  version: versionWithTool,
  state: 'Started',
  owner: user,
  download_in_progress: false,
  connection_method: connectionMethod,
};

export const LoadingStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () => new MockUserSessionService(),
        },
      ],
    }),
  ],
};

export const NoActiveStories: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () => new MockUserSessionService(undefined, true),
        },
      ],
    }),
  ],
};

export const SessionSuccessStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Started'),
            ),
        },
      ],
    }),
  ],
};

export const SessionWarningStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Created'),
            ),
        },
      ],
    }),
  ],
};

export const SessionErrorStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Failed'),
            ),
        },
      ],
    }),
  ],
};

export const SessionUnknownStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('unknown'),
            ),
        },
      ],
    }),
  ],
};

export const ReadonlySessionSuccessStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () => new MockUserSessionService(successReadonlySession),
        },
      ],
    }),
  ],
};
