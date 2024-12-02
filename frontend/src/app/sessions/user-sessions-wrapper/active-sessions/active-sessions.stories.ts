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
import { userEvent, within } from '@storybook/test';
import MockDate from 'mockdate';
import { Observable, of } from 'rxjs';
import { Session, SessionState } from 'src/app/openapi';
import { mockProject } from 'src/storybook/project';
import {
  mockPersistentSession,
  mockReadonlySession,
  mockTrainingSession,
} from 'src/storybook/session';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { UserSessionService } from '../../service/user-session.service';
import { ActiveSessionsComponent } from './active-sessions.component';

class MockUserSessionService implements Partial<UserSessionService> {
  public readonly sessions$: Observable<Session[] | undefined> = of(undefined);

  constructor(sessions?: Session[]) {
    this.sessions$ = of(sessions);
  }
}

const mockUserSessionServiceProvider = (sessions?: Session[]) => {
  return {
    provide: UserSessionService,
    useValue: new MockUserSessionService(sessions),
  };
};

const meta: Meta<ActiveSessionsComponent> = {
  title: 'Session Components/Active Sessions',
  component: ActiveSessionsComponent,
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
type Story = StoryObj<ActiveSessionsComponent>;

export const Loading: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockUserSessionServiceProvider()],
    }),
  ],
};

export const NoActiveStories: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockUserSessionServiceProvider([])],
    }),
  ],
};

export const FewActiveSessions: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockUserSessionServiceProvider([
          mockPersistentSession,
          mockReadonlySession,
        ]),
      ],
    }),
  ],
};

export const GroupedByProjectSessions: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockUserSessionServiceProvider([
          mockReadonlySession,
          { ...mockPersistentSession, project: mockProject },
          {
            ...mockPersistentSession,
            project: mockProject,
          },
        ]),
      ],
    }),
  ],
};

export const GroupedByTrainingSessions: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockUserSessionServiceProvider([
          mockReadonlySession,
          mockTrainingSession,
          {
            ...mockPersistentSession,
            project: mockProject,
            state: SessionState.Pending,
          },
        ]),
      ],
    }),
  ],
};

export const GroupedByTrainingSessionsExpanded: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockUserSessionServiceProvider([
          mockReadonlySession,
          mockTrainingSession,
          {
            ...mockPersistentSession,
            project: mockProject,
            state: SessionState.Pending,
          },
        ]),
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const training = canvas.getByTestId('training-expansion-1');
    await userEvent.click(training);
  },
};
