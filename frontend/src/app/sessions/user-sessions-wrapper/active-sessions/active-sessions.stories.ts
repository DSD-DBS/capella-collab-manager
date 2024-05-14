/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { Observable, of } from 'rxjs';
import { Session } from 'src/app/openapi';

import {
  createPersistentSessionWithState,
  mockSuccessReadonlySession,
} from 'src/storybook/session';
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
          useFactory: () =>
            new MockUserSessionService(mockSuccessReadonlySession),
        },
      ],
    }),
  ],
};
