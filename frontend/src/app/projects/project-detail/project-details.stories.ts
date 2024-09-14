/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { MockProjectUserService } from 'src/storybook/project-users';
import { ProjectDetailsComponent } from './project-details.component';

const meta: Meta<ProjectDetailsComponent> = {
  title: 'Project Components/Project Details',
  component: ProjectDetailsComponent,
  parameters: {
    chromatic: { viewports: [1920] },
  },
};

export default meta;
type Story = StoryObj<ProjectDetailsComponent>;

export const Loading: Story = {
  args: {},
};

export const LoadingAsProjectLead: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('manager'),
        },
      ],
    }),
  ],
};
