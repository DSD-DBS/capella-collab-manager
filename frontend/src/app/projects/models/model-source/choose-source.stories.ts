/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockModel,
  mockModelWrapperServiceProvider,
} from 'src/storybook/model';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { ChooseSourceComponent } from './choose-source.component';

const meta: Meta<ChooseSourceComponent> = {
  title: 'Model Components/Choose Source',
  component: ChooseSourceComponent,
};

export default meta;
type Story = StoryObj<ChooseSourceComponent>;

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(mockProject),
        mockModelWrapperServiceProvider(mockModel),
      ],
    }),
  ],
};

export const WithTeamSupport: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(mockProject),
        mockModelWrapperServiceProvider(mockModel),
        mockOwnUserWrapperServiceProvider({
          ...mockUser,
          role: 'administrator',
        }),
      ],
    }),
  ],
};
