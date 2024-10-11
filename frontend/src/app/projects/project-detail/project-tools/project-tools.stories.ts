/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import {
  mockProjectTool,
  projectToolServiceProvider,
} from 'src/storybook/project-tools';
import { mockProjectUserServiceProvider } from 'src/storybook/project-users';
import { mockCapellaTool, mockCapellaToolVersion } from 'src/storybook/tool';
import { ProjectToolsComponent } from './project-tools.component';

const meta: Meta<ProjectToolsComponent> = {
  title: 'Project Components/Used Tools',
  component: ProjectToolsComponent,
};

export default meta;
type Story = StoryObj<ProjectToolsComponent>;

export const Loading: Story = {
  args: {},
};

export const LoadingAsProjectLead: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectUserServiceProvider('manager', undefined, undefined),
      ],
    }),
  ],
};

export const ArchivedProject: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(
          { ...mockProject, is_archived: true },
          undefined,
        ),
        mockProjectUserServiceProvider('manager', undefined, undefined),
      ],
    }),
  ],
};

const projectTools = [
  mockProjectTool,
  {
    id: 1,
    tool: { ...mockCapellaTool, name: 'Example Tool' },
    tool_version: { ...mockCapellaToolVersion, name: '1.0.0' },
    used_by: [],
  },
  {
    id: null,
    tool: { ...mockCapellaTool, name: 'Tool 3' },
    tool_version: { ...mockCapellaToolVersion, name: 'Latest' },
    used_by: [],
  },
];

export const Loaded: Story = {
  decorators: [
    moduleMetadata({
      providers: [projectToolServiceProvider(projectTools)],
    }),
  ],
};

export const LoadedAsProjectLead: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        projectToolServiceProvider(projectTools),
        mockProjectUserServiceProvider('manager', undefined, undefined),
      ],
    }),
  ],
};
