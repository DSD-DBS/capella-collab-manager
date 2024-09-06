/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import { InputDialogComponent } from './input-dialog.component';

const meta: Meta<InputDialogComponent> = {
  title: 'Helpers / Input Dialog',
  component: InputDialogComponent,
};

export default meta;
type Story = StoryObj<InputDialogComponent>;

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            title: 'This is the title of the Input Dialog',
            text: 'This is the text of the Input Dialog',
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};
