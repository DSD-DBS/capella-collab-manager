/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { mockUser, MockUserService } from 'src/storybook/user';
import { UserWorkspacesComponent } from './user-workspaces.component';

const meta: Meta<UserWorkspacesComponent> = {
  title: 'Settings Components / Users Profile / User Workspaces',
  component: UserWorkspacesComponent,
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
  args: {
    _user: { ...mockUser, id: 0 },
  },
};

export default meta;
type Story = StoryObj<UserWorkspacesComponent>;

export const Loading: Story = {
  args: {},
};

export const NoWorkspaces: Story = {
  args: {
    workspaces: [],
  },
};

export const Workspace: Story = {
  args: {
    workspaces: [
      {
        id: 1,
        pvc_name: 'persistent-volume-429d805a-6904-4217-b035-8e3def3506ce',
        size: '20Gi',
      },
    ],
  },
};
