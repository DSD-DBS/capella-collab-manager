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
import { GitInstancesComponent } from './git-instances.component';

const meta: Meta<GitInstancesComponent> = {
  title: 'Settings Components/Modelsources/Git/Instances',
  component: GitInstancesComponent,
};

export default meta;
type Story = StoryObj<GitInstancesComponent>;

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
