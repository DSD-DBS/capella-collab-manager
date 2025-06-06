/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockUser } from 'src/storybook/user';
import { AddTagsDialogComponent } from './add-tags-dialog.component';

const meta: Meta<AddTagsDialogComponent> = {
  title: 'Settings Components/Add Tags Dialog',
  component: AddTagsDialogComponent,
  decorators: [dialogWrapper],
};

export default meta;
type Story = StoryObj<AddTagsDialogComponent>;

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: mockUser,
        },
      ],
    }),
  ],
};
