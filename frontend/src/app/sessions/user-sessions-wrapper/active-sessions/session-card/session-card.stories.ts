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
import MockDate from 'mockdate';
import { SessionPreparationState, SessionState } from 'src/app/openapi';
import {
  mockFeedbackConfig,
  mockFeedbackWrapperServiceProvider,
} from 'src/storybook/feedback';
import {
  mockPersistentSession,
  mockReadonlySession,
} from 'src/storybook/session';
import { mockHttpConnectionMethod } from 'src/storybook/tool';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { SessionCardComponent } from './session-card.component';

const meta: Meta<SessionCardComponent> = {
  title: 'Session Components/Session Card',
  component: SessionCardComponent,
  decorators: [
    moduleMetadata({
      providers: [mockOwnUserWrapperServiceProvider(mockUser)],
    }),
    componentWrapperDecorator(
      (story) => `<div class="w-full sm:w-[450px]">${story}</div>`,
    ),
  ],
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
};

export default meta;
type Story = StoryObj<SessionCardComponent>;

export const SessionNotFoundState: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.NotFound,
      state: SessionState.NotFound,
    },
  },
};

export const SessionPreparationPendingState: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.Pending,
      state: SessionState.Pending,
    },
  },
};

export const SessionPreparationRunningState: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.Running,
      state: SessionState.Pending,
    },
  },
};

export const SessionRunningState: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.Completed,
      state: SessionState.Running,
    },
  },
};

export const SessionTerminatingSoon: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.Completed,
      state: SessionState.Running,
      idle_state: {
        available: true,
        terminate_after_minutes: 90,
        idle_for_minutes: 80,
        unavailable_reason: null,
      },
    },
  },
};

export const SessionTerminatedState: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.Completed,
      state: SessionState.Terminated,
    },
  },
};

export const SessionPendingState: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.Completed,
      state: SessionState.Pending,
    },
  },
};

export const SessionFailedState: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.Completed,
      state: SessionState.Failed,
    },
  },
};

export const SessionUnknownState: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      preparation_state: SessionPreparationState.Completed,
      state: SessionState.Unknown,
    },
  },
};

export const SessionWithFeedbackEnabled: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
    },
  },
  decorators: [
    moduleMetadata({
      providers: [mockFeedbackWrapperServiceProvider(mockFeedbackConfig)],
    }),
  ],
};

export const ReadonlySessionSuccessState: Story = {
  args: {
    session: {
      selected: false,
      ...mockReadonlySession,
    },
  },
};

export const SessionSharingEnabled: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      connection_method: {
        ...mockHttpConnectionMethod,
        sharing: { enabled: true },
      },
    },
  },
};

export const SessionSharedWithUser: Story = {
  args: {
    session: {
      selected: false,
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
            blocked: false,
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
            blocked: false,
          },
          created_at: '2024-04-29T15:00:00Z',
        },
      ],
    },
  },
};
export const SessionSharedWithUserTerminatingSoon: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
      connection_method: {
        ...mockHttpConnectionMethod,
        sharing: { enabled: true },
      },
      idle_state: {
        available: true,
        terminate_after_minutes: 90,
        idle_for_minutes: 80,
        unavailable_reason: null,
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
            blocked: false,
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
            blocked: false,
          },
          created_at: '2024-04-29T15:00:00Z',
        },
      ],
    },
  },
};

export const SharedSession: Story = {
  args: {
    session: {
      selected: false,
      ...mockPersistentSession,
    },
  },
  decorators: [
    moduleMetadata({
      providers: [mockOwnUserWrapperServiceProvider({ ...mockUser, id: 2 })],
    }),
  ],
};
