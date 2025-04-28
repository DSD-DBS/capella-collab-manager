/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpEvent, HttpResponse } from '@angular/common/module.d-CnjH8Dlt';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { Observable, of } from 'rxjs';
import { EventsService, EventType, HistoryEvent } from 'src/app/openapi';
import { mockProject } from 'src/storybook/project';
import { mockUser } from 'src/storybook/user';
import { EventsComponent } from './events.component';

const meta: Meta<EventsComponent> = {
  title: 'General Components/Events',
  component: EventsComponent,
};

export default meta;
type Story = StoryObj<EventsComponent>;

class MockEventsService implements Partial<EventsService> {
  public getEvents(): Observable<HistoryEvent[]>;
  public getEvents(): Observable<HttpResponse<HistoryEvent[]>>;
  public getEvents(): Observable<HttpEvent<HistoryEvent[]>>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public getEvents(): Observable<any> {
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

export const NoEvents: Story = {
  args: {},
};

export const WithEvents: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: EventsService,
          useFactory: () => new MockEventsService(),
        },
      ],
    }),
  ],
};
