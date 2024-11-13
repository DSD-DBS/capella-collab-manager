/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from '../../../storybook/project';
import {
  mockProjectUsers,
  mockProjectUserServiceProvider,
} from '../../../storybook/project-users';
import { CreateProjectComponent } from './create-project.component';

const meta: Meta<CreateProjectComponent> = {
  title: 'Project Components/Create Project',
  component: CreateProjectComponent,
};

export default meta;
type Story = StoryObj<CreateProjectComponent>;

export const CreateProject: Story = {
  args: {},
};

export const AddTeamMembers: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(mockProject, [mockProject]),
        mockProjectUserServiceProvider('user', undefined, mockProjectUsers),
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const nameField = canvas.getByTestId('input-name');
    await userEvent.type(nameField, 'Test Project');
    const createProject = canvas.getByTestId('button-create-project');
    await userEvent.click(createProject);
  },
  parameters: {
    screenshot: {
      delay: 1000,
    },
  },
};

export const AddModel: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(mockProject, [mockProject]),
        mockProjectUserServiceProvider('user', undefined, mockProjectUsers),
      ],
    }),
  ],
  play: async (context) => {
    const canvas = within(context.canvasElement);
    await AddTeamMembers.play!(context);
    const skipMembers = canvas.getByTestId('button-skipAddMembers');
    await userEvent.click(skipMembers);
  },
  parameters: {
    screenshot: {
      delay: 1000,
    },
  },
};
