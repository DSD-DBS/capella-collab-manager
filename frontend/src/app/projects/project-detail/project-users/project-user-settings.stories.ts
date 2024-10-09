/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import {
  mockProjectUsers,
  MockProjectUserService,
} from 'src/storybook/project-users';
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
            new MockProjectUserService('user', undefined, mockProjectUsers),
        },
      ],
    }),
  ],
};
