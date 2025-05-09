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
            id: 2,
            name: 'Internal project',
            visibility: 'internal',
          },
          {
            ...mockProject,
            id: 3,
            name: 'Private project',
            visibility: 'private',
          },
          {
            ...mockProject,
            id: 4,
            name: 'Training project',
            type: 'training',
          },
          {
            ...mockProject,
            id: 5,
            name: 'Project with more users',
            users: {
              leads: 16,
              contributors: 24,
              subscribers: 106,
            },
          },
          {
            ...mockProject,
            id: 6,
            name: 'Archived project',
            is_archived: true,
          },
          {
            ...mockProject,
            id: 7,
            name: 'Project without description',
            description: '',
          },
          {
            ...mockProject,
            id: 8,
            name: 'This is a very long project name. Why would someone name a project like this?',
            is_archived: true,
          },
        ]),
      ],
    }),
  ],
};
