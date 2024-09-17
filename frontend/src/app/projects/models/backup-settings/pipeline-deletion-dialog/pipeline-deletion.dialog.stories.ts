/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { mockBackup } from 'src/storybook/backups';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockUser, MockUserService } from 'src/storybook/user';
import { PipelineDeletionDialogComponent } from './pipeline-deletion-dialog.component';

const meta: Meta<PipelineDeletionDialogComponent> = {
  title: 'Pipeline Components/Pipeline Deletion Dialog',
  component: PipelineDeletionDialogComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            projectSlug: 'test',
            modelSlug: 'test',
            backup: mockBackup,
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export default meta;
type Story = StoryObj<PipelineDeletionDialogComponent>;

export const AsProjectAdmin: Story = {
  args: {},
};

export const RequestSent: Story = {
  args: { loading: new BehaviorSubject(true) },
};

export const AsAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserWrapperService,
          useFactory: () =>
            new MockUserService({ ...mockUser, role: 'administrator' }),
        },
      ],
    }),
  ],
};
