/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockProject } from 'src/storybook/project';
import { AddUserToProjectDialogComponent } from './add-user-to-project.component';

const meta: Meta<AddUserToProjectDialogComponent> = {
  title: 'Project Components/Add User',
  component: AddUserToProjectDialogComponent,
  decorators: [dialogWrapper],
};

export default meta;
type Story = StoryObj<AddUserToProjectDialogComponent>;

export const Dialog: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            project: mockProject,
          },
        },
      ],
    }),
  ],
};
