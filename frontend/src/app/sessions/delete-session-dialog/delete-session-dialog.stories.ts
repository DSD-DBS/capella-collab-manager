/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import {
  mockPersistentSession,
  mockReadonlySession,
  mockTrainingSession,
} from 'src/storybook/session';
import { DeleteSessionDialogComponent } from './delete-session-dialog.component';

const meta: Meta<DeleteSessionDialogComponent> = {
  title: 'Session Components/Delete Session Dialog',
  component: DeleteSessionDialogComponent,
  decorators: [dialogWrapper],
};

export default meta;
type Story = StoryObj<DeleteSessionDialogComponent>;

export const OneSession: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: [mockPersistentSession],
        },
      ],
    }),
  ],
};

export const MultipleSession: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: [
            mockPersistentSession,
            mockTrainingSession,
            mockReadonlySession,
          ],
        },
      ],
    }),
  ],
};
