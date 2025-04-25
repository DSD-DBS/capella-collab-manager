/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockProjectUsers,
  mockProjectUserServiceProvider,
} from 'src/storybook/project-users';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { ProjectUserSettingsComponent } from './project-user-settings.component';

const meta: Meta<ProjectUserSettingsComponent> = {
  title: 'Project Components/Project Users',
  component: ProjectUserSettingsComponent,
};

export default meta;
type Story = StoryObj<ProjectUserSettingsComponent>;

export const Loading: Story = {
  args: {},
};

const currentUser = {
  ...mockUser,
  id: 45,
  name: 'currentUser',
};

export const Overview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectUserServiceProvider('user', undefined, [
          ...mockProjectUsers,
          {
            role: 'manager',
            permission: 'write',
            user: currentUser,
          },
        ]),
        mockOwnUserWrapperServiceProvider(currentUser),
      ],
    }),
  ],
};
