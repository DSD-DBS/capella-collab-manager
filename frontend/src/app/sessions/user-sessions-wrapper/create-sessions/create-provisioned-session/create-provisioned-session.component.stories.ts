/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { mockSimpleToolModelWithoutProject } from 'src/storybook/model';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { mockProjectTool, mockTrainingTool } from 'src/storybook/project-tools';
import { CreateProvisionedSessionComponent } from './create-provisioned-session.component';

const meta: Meta<CreateProvisionedSessionComponent> = {
  title: 'Session Components/Create Provisioned Session',
  component: CreateProvisionedSessionComponent,
};

export default meta;
type Story = StoryObj<CreateProvisionedSessionComponent>;

export const Loading: Story = {
  args: {},
};

export const LoadedProjectWithoutTools: Story = {
  args: {
    provisioningPerTool: [],
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectWrapperServiceProvider(mockProject)],
    }),
  ],
};

export const LoadedProjectWithoutModels: Story = {
  args: {
    provisioningPerTool: [
      {
        ...mockProjectTool,
        used_by: [],
      },
    ],
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectWrapperServiceProvider(mockProject)],
    }),
  ],
};

const toolProvisioning = {
  ...mockSimpleToolModelWithoutProject,
  provisioning: null,
};

const coffeeMachineProvisioning = {
  id: 2,
  slug: 'coffee-machine',
  name: 'Coffee machine',
  git_models: [],
  provisioning: {
    session: null,
    provisioned_at: '2024-04-29T14:00:00Z',
    revision: 'main',
    commit_hash: 'db45166576e7f1e7fec3256e8657ba431f9b5b77',
  },
};

export const LoadedProject: Story = {
  args: {
    provisioningPerTool: [
      {
        ...mockProjectTool,
        used_by: [toolProvisioning, coffeeMachineProvisioning],
      },
    ],
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectWrapperServiceProvider(mockProject)],
    }),
  ],
};

export const LoadedProjectContinue: Story = {
  args: {
    provisioningPerTool: [
      {
        ...mockProjectTool,
        used_by: [coffeeMachineProvisioning],
      },
    ],
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectWrapperServiceProvider(mockProject)],
    }),
  ],
};

export const LoadedTraining: Story = {
  args: {
    provisioningPerTool: [
      {
        ...mockProjectTool,
        used_by: [],
      },
      {
        ...mockTrainingTool,
        used_by: [
          {
            id: 3,
            slug: 'pvmt-training',
            name: 'PVMT Training',
            git_models: [],
            provisioning: null,
          },
        ],
      },
    ],
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider({ ...mockProject, type: 'training' }),
      ],
    }),
  ],
};
