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
import { EventType, HistoryEvent } from '../../../../openapi';
import { Page, PageWrapper } from '../../../../schemes';
import { ProjectAuditLogComponent } from './project-audit-log.component';
import { ProjectAuditLogService } from './service/project-audit-log.service';

const meta: Meta<ProjectAuditLogComponent> = {
  title: 'Project Components / Audit Log',
  component: ProjectAuditLogComponent,
};

export default meta;
type Story = StoryObj<ProjectAuditLogComponent>;

const mockHistoryEvents: Page<HistoryEvent> = {
  items: [
    {
      id: 1,
      execution_time: new Date(2024, 1, 1).toISOString(),
      event_type: EventType.CreatedUser,
      user: mockUser,
      executor: mockUser,
      project: mockProject,
      reason: 'Another Test Reason',
    },
    {
      id: 2,
      execution_time: new Date(2024, 1, 1).toISOString(),
      event_type: EventType.AssignedProjectPermissionReadOnly,
      user: mockUser,
      executor: mockUser,
      project: mockProject,
      reason: 'Test Reason',
    },
    {
      id: 3,
      execution_time: new Date(2024, 1, 1).toISOString(),
      event_type: EventType.CreatedUser,
      user: mockUser,
      executor: mockUser,
      project: mockProject,
      reason: 'Test Reason',
    },
    {
      id: 4,
      execution_time: new Date(2024, 1, 1).toISOString(),
      event_type: EventType.RemovedFromProject,
      user: mockUser,
      executor: mockUser,
      project: mockProject,
      reason: 'Test Reason',
    },
    {
      id: 5,
      execution_time: new Date(2024, 1, 1).toISOString(),
      event_type: EventType.AddedToProject,
      user: mockUser,
      executor: mockUser,
      project: mockProject,
      reason: 'Test Reason',
    },
  ],
  total: 5,
  page: 1,
  size: 5,
  pages: 1,
};

class MockProjectAuditLogService implements Partial<ProjectAuditLogService> {
  private _projectHistoryEventPages = new BehaviorSubject<
    PageWrapper<HistoryEvent>
  >({
    pages: [mockHistoryEvents],
    total: 1,
  });
  public readonly projectHistoryEventsPages$ =
    this._projectHistoryEventPages.asObservable();

  constructor(historyEvents: Page<HistoryEvent>) {
    this._projectHistoryEventPages.next({
      pages: [historyEvents],
      total: 1,
    });
  }
}

export const Loading: Story = {
  args: {},
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

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: [],
        },
        {
          provide: ProjectAuditLogService,
          useFactory: () => new MockProjectAuditLogService(mockHistoryEvents),
        },
      ],
    }),
    dialogWrapper,
  ],
};
