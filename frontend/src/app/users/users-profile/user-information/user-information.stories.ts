/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpEvent, HttpResponse } from '@angular/common/http';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import MockDate from 'mockdate';
import { Observable, of } from 'rxjs';
import { EventType, HistoryEvent, UsersService } from 'src/app/openapi';
import { mockProject } from 'src/storybook/project';
import {
  mockUser,
  mockOwnUserWrapperServiceProvider,
  mockUserWrapperServiceProvider,
} from 'src/storybook/user';
import { UserInformationComponent } from './user-information.component';

const meta: Meta<UserInformationComponent> = {
  title: 'Settings Components/Users Profile/User Information',
  component: UserInformationComponent,
  decorators: [
    moduleMetadata({
      providers: [
        mockOwnUserWrapperServiceProvider({
          ...mockUser,
          role: 'administrator',
        }),
        mockUserWrapperServiceProvider({ ...mockUser, id: 0 }),
      ],
    }),
  ],
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
};

export default meta;
type Story = StoryObj<UserInformationComponent>;

export const NoEvents: Story = {
  args: {
    userEvents: [],
  },
};

export const LoadingEvents: Story = {
  args: {},
};

class MockUsersService implements Partial<UsersService> {
  public getUserEvents(_userId: number): Observable<HistoryEvent[]>;
  public getUserEvents(
    _userId: number,
  ): Observable<HttpResponse<HistoryEvent[]>>;
  public getUserEvents(_userId: number): Observable<HttpEvent<HistoryEvent[]>>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public getUserEvents(_userId: number): Observable<any> {
    return of([
      {
        user: mockUser,
        executor: null,
        project: mockProject,
        execution_time: '2023-04-25T11:08:24.286648Z',
        event_type: EventType.CreatedUser,
        reason: 'User is very important.',
        id: 1,
      },
      {
        user: mockUser,
        executor: mockUser,
        project: mockProject,
        execution_time: '2023-04-25T11:08:24.286648Z',
        event_type: EventType.AddedToProject,
        reason: 'User is very important.',
        id: 1,
      },
      {
        user: mockUser,
        executor: mockUser,
        project: mockProject,
        execution_time: '2023-04-25T12:08:24.286648Z',
        event_type: EventType.AssignedProjectPermissionReadWrite,
        reason: 'User is very important.',
        id: 2,
      },
      {
        user: mockUser,
        executor: mockUser,
        project: mockProject,
        execution_time: '2023-04-25T12:08:24.286648Z',
        event_type: EventType.RemovedFromProject,
        reason: "User doesn't work for the project anymore.",
        id: 3,
      },
    ]);
  }
}

export const EventsAndLastLogin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UsersService,
          useFactory: () => new MockUsersService(),
        },
      ],
    }),
  ],
};
