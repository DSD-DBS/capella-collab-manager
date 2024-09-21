/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { MockProjectUserService } from 'src/storybook/project-users';
import { mockUser } from 'src/storybook/user';
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

export const Overview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectUserService,
          useFactory: () =>
            new MockProjectUserService('user', undefined, [
              {
                role: 'administrator',
                permission: 'write',
                user: { ...mockUser, name: 'administrator1' },
              },
              {
                role: 'administrator',
                permission: 'write',
                user: { ...mockUser, name: 'administrator2' },
              },
              {
                role: 'user',
                permission: 'write',
                user: { ...mockUser, name: 'projectuser1' },
              },
              {
                role: 'user',
                permission: 'read',
                user: { ...mockUser, name: 'projectuserWithReallyLongName' },
              },
              {
                role: 'manager',
                permission: 'write',
                user: { ...mockUser, name: 'projectadmin1' },
              },
            ]),
        },
      ],
    }),
  ],
};
