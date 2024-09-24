/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { GitInstancesWrapperService } from 'src/app/settings/modelsources/git-settings/service/git-instances.service';
import {
  mockGitHubInstance,
  mockGitInstance,
  MockGitInstancesService,
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
      providers: [
        {
          provide: GitInstancesWrapperService,
          useFactory: () => new MockGitInstancesService(mockGitInstance),
        },
      ],
    }),
  ],
};

export const Github: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: GitInstancesWrapperService,
          useFactory: () => new MockGitInstancesService(mockGitHubInstance),
        },
      ],
    }),
  ],
};
