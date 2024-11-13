/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { ProjectOverviewComponent } from './project-overview.component';

const meta: Meta<ProjectOverviewComponent> = {
  title: 'Project Components/Project Overview',
  component: ProjectOverviewComponent,
};

export default meta;
type Story = StoryObj<ProjectOverviewComponent>;

export const Loading: Story = {
  args: {},
};

export const Overview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(undefined, [
          {
            ...mockProject,
            name: 'Internal project',
            visibility: 'internal',
          },
          {
            ...mockProject,
            name: 'Private project',
            visibility: 'private',
          },
          {
            ...mockProject,
            name: 'Training project',
            type: 'training',
          },
          {
            ...mockProject,
            name: 'Project with more users',
            users: {
              leads: 16,
              contributors: 24,
              subscribers: 106,
            },
          },
          {
            ...mockProject,
            name: 'Archived project',
            is_archived: true,
          },
          {
            ...mockProject,
            name: 'Project without description',
            description: '',
          },
        ]),
      ],
    }),
  ],
};
