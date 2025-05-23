/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockGitHubInstance,
  mockGitInstance,
  mockGitInstancesServiceProvider,
} from 'src/storybook/git';
import { EditGitInstanceComponent } from './edit-git-instance.component';

const meta: Meta<EditGitInstanceComponent> = {
  title: 'Settings Components/Modelsources/Git/Edit Instance',
  component: EditGitInstanceComponent,
};

export default meta;
type Story = StoryObj<EditGitInstanceComponent>;

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockGitInstancesServiceProvider(mockGitInstance)],
    }),
  ],
};

export const GitHub: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockGitInstancesServiceProvider(mockGitHubInstance)],
    }),
  ],
};
