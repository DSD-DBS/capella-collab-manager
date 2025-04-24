/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { CreateProjectToolsComponent } from './create-project-tools.component';

const meta: Meta<CreateProjectToolsComponent> = {
  title: 'Project Components/Create Project Tools',
  component: CreateProjectToolsComponent,
};

export default meta;
type Story = StoryObj<CreateProjectToolsComponent>;

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockProjectWrapperServiceProvider(mockProject)],
    }),
  ],
};
