/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import { ConfirmationDialogComponent } from './confirmation-dialog.component';

const meta: Meta<ConfirmationDialogComponent> = {
  title: 'Helpers / Confirmation Dialog',
  component: ConfirmationDialogComponent,
};

export default meta;
type Story = StoryObj<ConfirmationDialogComponent>;

export const WithRequiredInput: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            title: 'This is the title of the Confirmation Dialog',
            text: 'Do you really want to continue with the action?',
            requiredInput: 'required input',
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export const WithoutRequiredInput: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            title: 'This is the title of the Confirmation Dialog',
            text: 'Do you really want to continue with the action?',
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export const WithHTML: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            title: 'This is the title of the Confirmation Dialog',
            text:
              'You can also use some basic HTML in the text. <br>' +
              '<b>This should be bold</b><br>' +
              "<a href='https://example.com' target='_blank'>This should be a link</a>",
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};
