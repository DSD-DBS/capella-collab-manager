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
import { Session } from 'src/app/openapi';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { FeedbackWrapperService } from 'src/app/sessions/feedback/feedback.service';
import {
  mockFeedbackConfig,
  MockFeedbackWrapperService,
} from 'src/storybook/feedback';
import {
  createPersistentSessionWithState,
  mockSuccessReadonlySession,
} from 'src/storybook/session';
import { mockHttpConnectionMethod } from 'src/storybook/tool';
import { MockUserService, mockUser } from 'src/storybook/user';
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
          provide: UserWrapperService,
          useFactory: () => new MockUserService(mockUser),
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

export const SessionKillingStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Killing'),
            ),
        },
      ],
    }),
  ],
};

export const SessionStoppedStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('ExceededGracePeriod'),
            ),
        },
      ],
    }),
  ],
};

export const SessionQueuedStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Preempting'),
            ),
        },
      ],
    }),
  ],
};

export const SessionNetworkIssuesStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('NetworkNotReady'),
            ),
        },
      ],
    }),
  ],
};

export const SessionPullingStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Pulling'),
            ),
        },
      ],
    }),
  ],
};

export const SessionPulledStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Pulled'),
            ),
        },
      ],
    }),
  ],
};

export const SessionScheduledStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Scheduled'),
            ),
        },
      ],
    }),
  ],
};

export const SessionFailedSchedulingStateStory: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('FailedScheduling'),
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

export const SessionWithFeedbackEnabled: Story = {
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
        {
          provide: FeedbackWrapperService,
          useFactory: () => new MockFeedbackWrapperService(mockFeedbackConfig),
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
          useFactory: () =>
            new MockUserSessionService(mockSuccessReadonlySession),
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
              ...createPersistentSessionWithState('Started'),
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
              ...createPersistentSessionWithState('Started'),
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
          useFactory: () =>
            new MockUserSessionService({
              ...createPersistentSessionWithState('Started'),
            }),
        },
        {
          provide: UserWrapperService,
          useFactory: () => new MockUserService({ ...mockUser, id: 2 }),
        },
      ],
    }),
  ],
};
