/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockGitHubInstance,
  mockGitInstance,
  mockGitInstancesServiceProvider,
  mockGitLabInstance,
} from 'src/storybook/git';
import { GitSettingsComponent } from './git-settings.component';

const meta: Meta<GitSettingsComponent> = {
  title: 'Settings Components/Modelsources/Git/Instances',
  component: GitSettingsComponent,
};

export default meta;
type Story = StoryObj<GitSettingsComponent>;

export const Loading: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockGitInstancesServiceProvider()],
    }),
  ],
};

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockGitInstancesServiceProvider(undefined, [
          mockGitLabInstance,
          mockGitHubInstance,
          mockGitInstance,
        ]),
      ],
    }),
  ],
};
