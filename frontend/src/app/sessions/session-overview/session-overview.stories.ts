/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { of } from 'rxjs';
import {
  Session,
  SessionPreparationState,
  SessionsService,
  SessionState,
} from 'src/app/openapi';
import {
  createPersistentSessionWithState,
  mockPersistentSession,
  mockReadonlySession,
} from 'src/storybook/session';
import { mockUser } from 'src/storybook/user';
import { SessionOverviewComponent } from './session-overview.component';

const meta: Meta<SessionOverviewComponent> = {
  title: 'Session Components/Session Overview',
  component: SessionOverviewComponent,
};

export default meta;
type Story = StoryObj<SessionOverviewComponent>;

class MockSessionsService {
  sessions: Session[] | undefined = undefined;

  getAllSessions() {
    return of(this.sessions ?? []);
  }

  constructor(sessions: Session[] | undefined) {
    this.sessions = sessions;
  }
}

export const Loading: Story = {
  args: {},
};

export const NoSessions: Story = {
  args: {
    sessions: [],
  },
};

const sessions = [
  mockPersistentSession,
  { ...mockReadonlySession, id: 'vjmczglcgeltbfcronujtelwx' },
  {
    ...createPersistentSessionWithState(
      SessionPreparationState.Failed,
      SessionState.Pending,
    ),
    owner: {
      ...mockUser,
      name: 'anotherUser',
    },
    id: 'cfgbrmirzwxpjwfkxszemtlpr',
  },
];

export const Overview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: SessionsService,
          useValue: new MockSessionsService(sessions),
        },
      ],
    }),
  ],
};

export const AllSelected: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: SessionsService,
          useValue: new MockSessionsService(sessions),
        },
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const checkbox = canvas.getByTestId('select-all-sessions');
    await userEvent.click(checkbox);
  },
};
