/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import { createPersistentSessionWithState } from 'src/storybook/session';
import { SessionSharingDialogComponent } from './session-sharing-dialog.component';

const meta: Meta<SessionSharingDialogComponent> = {
  title: 'Session Components/Session Sharing Dialog',
  component: SessionSharingDialogComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: createPersistentSessionWithState('running'),
        },
      ],
    }),
    dialogWrapper,
  ],
};

export default meta;
type Story = StoryObj<SessionSharingDialogComponent>;

export const Default: Story = {
  args: {
    users: [
      {
        username: 'user-already-added',
        state: 'success',
        tooltip: 'The session has been shared with the user.',
      },
      {
        username: 'user-adding-failed',
        state: 'error',
        tooltip: "The user couldn't be added.",
      },
      {
        username: 'user-creation-pending',
        state: 'pending',
        tooltip: 'Submit the form to add the user.',
      },
    ],
  },
};
