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
import { EditGitSettingsComponent } from './edit-git-settings.component';

const meta: Meta<EditGitSettingsComponent> = {
  title: 'Settings Components/Modelsources/Git/Edit Instance',
  component: EditGitSettingsComponent,
};

export default meta;
type Story = StoryObj<EditGitSettingsComponent>;

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockGitInstancesServiceProvider(mockGitInstance)],
    }),
  ],
};

export const Github: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockGitInstancesServiceProvider(mockGitHubInstance)],
    }),
  ],
};
