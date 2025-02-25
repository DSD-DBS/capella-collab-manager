/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import MockDate from 'mockdate';
import { of } from 'rxjs';
import {
  Session,
  SessionPreparationState,
  SessionsService,
  SessionState,
} from 'src/app/openapi';
import {
  mockPersistentSession,
  mockReadonlySession,
} from 'src/storybook/session';
import { mockUser } from 'src/storybook/user';
import { SessionOverviewComponent } from './session-overview.component';

const meta: Meta<SessionOverviewComponent> = {
  title: 'Session Components/Session Overview',
  component: SessionOverviewComponent,
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
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
    ...mockPersistentSession,
    created_at: '2024-04-30T12:00:00Z',
    preparation_state: SessionPreparationState.Failed,
    state: SessionState.Pending,
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
