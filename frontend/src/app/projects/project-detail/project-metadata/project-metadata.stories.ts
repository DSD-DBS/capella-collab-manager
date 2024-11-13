/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { mockProject } from 'src/storybook/project';
import { mockProjectUserServiceProvider } from 'src/storybook/project-users';
import { ProjectMetadataComponent } from './project-metadata.component';

const meta: Meta<ProjectMetadataComponent> = {
  title: 'Project Components/Project Metadata',
  component: ProjectMetadataComponent,
};

export default meta;
type Story = StoryObj<ProjectMetadataComponent>;

export const Loading: Story = {
  args: {
    project: undefined,
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectUserServiceProvider('user')],
    }),
  ],
};

export const NormalUser: Story = {
  args: {
    project: mockProject,
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectUserServiceProvider('user')],
    }),
  ],
};

export const ProjectAdmin: Story = {
  args: {
    project: mockProject,
    canDelete: true,
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectUserServiceProvider('manager')],
    }),
  ],
};

export const NormalUserArchived: Story = {
  args: {
    project: { ...mockProject, is_archived: true },
    canDelete: true,
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectUserServiceProvider('user')],
    }),
  ],
};

export const ProjectAdminArchived: Story = {
  args: {
    project: { ...mockProject, is_archived: true },
    canDelete: true,
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectUserServiceProvider('manager')],
    }),
  ],
};

export const CantDelete: Story = {
  args: {
    project: mockProject,
    canDelete: false,
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectUserServiceProvider('manager')],
    }),
  ],
};
