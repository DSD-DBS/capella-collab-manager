/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { dialogWrapper } from 'src/storybook/decorators';
import { startedSession } from 'src/storybook/session';
import { mockTool } from 'src/storybook/tool';
import { MockUserService, mockUser } from 'src/storybook/user';
import { ConnectionDialogComponent } from './connection-dialog.component';

const meta: Meta<ConnectionDialogComponent> = {
  title: 'Session Components / Connection Dialog',
  component: ConnectionDialogComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: startedSession,
        },
      ],
    }),
    dialogWrapper,
  ],
};

export default meta;
type Story = StoryObj<ConnectionDialogComponent>;

export const WithoutTeamForCapella: Story = {
  args: {
    connectionInfo: {
      local_storage: {},
      t4c_token: '',
      redirect_url: 'https://example.com',
    },
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            ...startedSession,
            version: {
              ...startedSession.version,
              tool: { ...mockTool, integrations: { t4c: false } },
            },
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export const SharedSession: Story = {
  args: {
    connectionInfo: {
      local_storage: {},
      t4c_token: '',
      redirect_url: 'https://example.com',
    },
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            ...startedSession,
            owner: { ...mockUser, id: '2' },
          },
        },
        {
          provide: UserWrapperService,
          useFactory: () => new MockUserService(mockUser),
        },
      ],
    }),
  ],
};

export const WithSessionToken: Story = {
  args: {
    connectionInfo: {
      local_storage: {},
      t4c_token: 'sessiontoken',
      redirect_url: 'https://example.com',
    },
  },
};

export const WithoutSessionToken: Story = {
  args: {
    connectionInfo: {
      local_storage: {},
      t4c_token: '',
      redirect_url: 'https://example.com',
    },
  },
};

export const LoadingSessionInfo: Story = {
  args: {},
};
