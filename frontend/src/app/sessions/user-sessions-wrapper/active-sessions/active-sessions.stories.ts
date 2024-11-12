/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  Meta,
  StoryObj,
  componentWrapperDecorator,
  moduleMetadata,
} from '@storybook/angular';
import { Observable, of } from 'rxjs';
import {
  Session,
  SessionPreparationState,
  SessionState,
} from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { FeedbackWrapperService } from 'src/app/sessions/feedback/feedback.service';
import {
  mockFeedbackConfig,
  MockFeedbackWrapperService,
} from 'src/storybook/feedback';
import {
  createPersistentSessionWithState,
  mockPersistentSession,
  mockReadonlySession,
} from 'src/storybook/session';
import { mockHttpConnectionMethod } from 'src/storybook/tool';
import { MockOwnUserWrapperService, mockUser } from 'src/storybook/user';
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
  title: 'Session Components/Active Sessions',
  component: ActiveSessionsComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: OwnUserWrapperService,
          useFactory: () => new MockOwnUserWrapperService(mockUser),
        },
      ],
    }),
    componentWrapperDecorator(
      (story) => `<div class="w-[360px] sm:w-[450px]">${story}</div>`,
    ),
  ],
};

export default meta;
type Story = StoryObj<ActiveSessionsComponent>;

export const Loading: Story = {
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

export const SessionNotFoundState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState(
                SessionPreparationState.NotFound,
                SessionState.NotFound,
              ),
            ),
        },
      ],
    }),
  ],
};

export const SessionPreparationPendingState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState(
                SessionPreparationState.Pending,
                SessionState.Pending,
              ),
            ),
        },
      ],
    }),
  ],
};

export const SessionPreparationRunningState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState(
                SessionPreparationState.Running,
                SessionState.Pending,
              ),
            ),
        },
      ],
    }),
  ],
};

export const SessionRunningState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState(
                SessionPreparationState.Completed,
                SessionState.Running,
              ),
            ),
        },
      ],
    }),
  ],
};

export const SessionTerminatedState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState(
                SessionPreparationState.Completed,
                SessionState.Terminated,
              ),
            ),
        },
      ],
    }),
  ],
};

export const SessionPendingState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState(
                SessionPreparationState.Completed,
                SessionState.Pending,
              ),
            ),
        },
      ],
    }),
  ],
};

export const SessionFailedState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState(
                SessionPreparationState.Completed,
                SessionState.Failed,
              ),
            ),
        },
      ],
    }),
  ],
};

export const SessionUnknownState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState(
                SessionPreparationState.Completed,
                SessionState.Unknown,
              ),
            ),
        },
      ],
    }),
  ],
};

export const SessionWithFeedbackEnabled: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () => new MockUserSessionService(mockPersistentSession),
        },
        {
          provide: FeedbackWrapperService,
          useFactory: () => new MockFeedbackWrapperService(mockFeedbackConfig),
        },
      ],
    }),
  ],
};

export const ReadonlySessionSuccessState: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () => new MockUserSessionService(mockReadonlySession),
        },
      ],
    }),
  ],
};

export const SessionSharingEnabled: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService({
              ...mockPersistentSession,
              connection_method: {
                ...mockHttpConnectionMethod,
                sharing: { enabled: true },
              },
            }),
        },
      ],
    }),
  ],
};

export const SessionSharedWithUser: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService({
              ...mockPersistentSession,
              connection_method: {
                ...mockHttpConnectionMethod,
                sharing: { enabled: true },
              },
              shared_with: [
                {
                  user: {
                    id: 1,
                    name: 'user_1',
                    role: 'administrator',
                    email: null,
                    idp_identifier: 'user_1',
                    beta_tester: false,
                  },
                  created_at: '2024-04-29T15:00:00Z',
                },
                {
                  user: {
                    id: 2,
                    name: 'user_2',
                    role: 'user',
                    email: null,
                    idp_identifier: 'user_2',
                    beta_tester: false,
                  },
                  created_at: '2024-04-29T15:00:00Z',
                },
              ],
            }),
        },
      ],
    }),
  ],
};

export const SharedSession: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () => new MockUserSessionService(mockPersistentSession),
        },
        {
          provide: OwnUserWrapperService,
          useFactory: () =>
            new MockOwnUserWrapperService({ ...mockUser, id: 2 }),
        },
      ],
    }),
  ],
};
