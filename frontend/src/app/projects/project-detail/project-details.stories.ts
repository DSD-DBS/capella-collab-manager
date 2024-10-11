/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { mockProjectUserServiceProvider } from 'src/storybook/project-users';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { ProjectDetailsComponent } from './project-details.component';

const meta: Meta<ProjectDetailsComponent> = {
  title: 'Project Components/Project Details',
  component: ProjectDetailsComponent,
};

export default meta;
type Story = StoryObj<ProjectDetailsComponent>;

export const Loading: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockOwnUserWrapperServiceProvider({ ...mockUser, beta_tester: true }),
      ],
    }),
  ],
};

export const LoadingAsProjectLead: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectUserServiceProvider('manager'),
        mockOwnUserWrapperServiceProvider({ ...mockUser, beta_tester: true }),
      ],
    }),
  ],
};

export const ProjectLoaded: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(mockProject, undefined),
        mockOwnUserWrapperServiceProvider({ ...mockUser, beta_tester: true }),
      ],
    }),
  ],
};

export const ProjectLoadedNonBeta: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockProjectWrapperServiceProvider(mockProject, undefined)],
    }),
  ],
};

export const TrainingLoaded: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(
          { ...mockProject, type: 'training' },
          undefined,
        ),
        mockOwnUserWrapperServiceProvider({ ...mockUser, beta_tester: true }),
      ],
    }),
  ],
};
