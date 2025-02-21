/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MatTableDataSource } from '@angular/material/table';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import MockDate from 'mockdate';
import { EventType, HistoryEvent } from 'src/app/openapi';
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

const events: HistoryEvent[] = [
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
];

export const EventsAndLastLogin: Story = {
  args: {
    userEvents: events,
    historyEventDataSource: new MatTableDataSource<HistoryEvent>(events),
  },
};
