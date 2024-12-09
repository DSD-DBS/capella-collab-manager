/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { dialogWrapper } from '../../../../../storybook/decorators';
import { mockProject } from '../../../../../storybook/project';
import { mockUser } from '../../../../../storybook/user';
import { EventType, PageHistoryEvent } from '../../../../openapi';
import { ProjectAuditLogComponent } from './project-audit-log.component';
import {
  PageHistoryEventWrapper,
  ProjectAuditLogService,
} from './project-audit-log.service';

const meta: Meta<ProjectAuditLogComponent> = {
  title: 'Project Components/Audit Log',
  component: ProjectAuditLogComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: [],
        },
      ],
    }),
    dialogWrapper,
  ],
};

export default meta;
type Story = StoryObj<ProjectAuditLogComponent>;

const mockHistoryEventBase = {
  execution_time: new Date(2024, 1, 1).toISOString(),
  user: mockUser,
  executor: mockUser,
  project: mockProject,
  reason: 'Test Reason',
};

const mockHistoryEvents: PageHistoryEvent = {
  items: [
    {
      ...mockHistoryEventBase,
      id: 1,
      event_type: EventType.CreatedUser,
      reason: 'Another Test Reason',
    },
    {
      ...mockHistoryEventBase,
      id: 2,
      event_type: EventType.AssignedProjectPermissionReadOnly,
    },
    {
      ...mockHistoryEventBase,
      id: 3,
      event_type: EventType.CreatedUser,
    },
    {
      ...mockHistoryEventBase,
      id: 4,
      event_type: EventType.RemovedFromProject,
    },
    {
      ...mockHistoryEventBase,
      id: 5,
      event_type: EventType.AddedToProject,
    },
  ],
  total: 5,
  page: 1,
  size: 5,
  pages: 1,
};

class MockProjectAuditLogService implements Partial<ProjectAuditLogService> {
  private _projectHistoryEventPages =
    new BehaviorSubject<PageHistoryEventWrapper>({
      pages: [mockHistoryEvents],
      total: 1,
    });
  public readonly projectHistoryEventsPages$ =
    this._projectHistoryEventPages.asObservable();

  constructor(historyEvents: PageHistoryEvent) {
    this._projectHistoryEventPages.next({
      pages: [historyEvents],
      total: 1,
    });
  }
}

export const Loading: Story = {
  args: {},
};

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectAuditLogService,
          useFactory: () => new MockProjectAuditLogService(mockHistoryEvents),
        },
      ],
    }),
  ],
};
