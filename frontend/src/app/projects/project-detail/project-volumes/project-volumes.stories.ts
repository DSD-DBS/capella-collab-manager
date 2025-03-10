/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import MockDate from 'mockdate';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { mockProjectUserServiceProvider } from 'src/storybook/project-users';
import { ProjectVolumesComponent } from './project-volumes.component';

const meta: Meta<ProjectVolumesComponent> = {
  title: 'Projects Components / Project Volumes',
  component: ProjectVolumesComponent,
  decorators: [
    moduleMetadata({
      providers: [mockProjectWrapperServiceProvider(mockProject)],
    }),
  ],
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
};

export default meta;
type Story = StoryObj<ProjectVolumesComponent>;

const mockProjectVolume = {
  id: 1,
  created_at: '2024-04-01T15:00:00Z',
  size: '2Gi',
  pvc_name: 'shared-workspace-1234',
};

export const Loading: Story = {
  args: {},
};

export const NoVolumeAsUser: Story = {
  args: {
    projectVolume: null,
  },
};

export const NoVolumeAsAdmin: Story = {
  args: {
    projectVolume: null,
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectUserServiceProvider('manager')],
    }),
  ],
};

export const VolumeAsUser: Story = {
  args: {
    projectVolume: mockProjectVolume,
  },
};

export const VolumeAsAdmin: Story = {
  args: {
    projectVolume: mockProjectVolume,
  },
  decorators: [
    moduleMetadata({
      providers: [mockProjectUserServiceProvider('manager')],
    }),
  ],
};
