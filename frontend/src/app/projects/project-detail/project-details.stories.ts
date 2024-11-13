/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { mockProjectUserServiceProvider } from 'src/storybook/project-users';
import { ProjectDetailsComponent } from './project-details.component';

const meta: Meta<ProjectDetailsComponent> = {
  title: 'Project Components/Project Details',
  component: ProjectDetailsComponent,
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
      providers: [mockProjectUserServiceProvider('manager')],
    }),
  ],
};
