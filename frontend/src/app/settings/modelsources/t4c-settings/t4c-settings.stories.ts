/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockT4CInstance,
  mockT4CInstanceWrapperServiceProvider,
  mockT4CLicenseServer,
  mockT4CLicenseServerWrapperServiceProvider,
} from 'src/storybook/t4c';
import { T4CSettingsComponent } from './t4c-settings.component';

const meta: Meta<T4CSettingsComponent> = {
  title: 'Settings Components/Modelsources/T4C/Server Overview',
  component: T4CSettingsComponent,
};

export default meta;
type Story = StoryObj<T4CSettingsComponent>;

export const Loading: Story = {
  args: {},
};

export const Overview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CInstanceWrapperServiceProvider(mockT4CInstance, [
          mockT4CInstance,
          { ...mockT4CInstance, is_archived: true },
        ]),
        mockT4CLicenseServerWrapperServiceProvider(mockT4CLicenseServer, [
          mockT4CLicenseServer,
        ]),
      ],
    }),
  ],
};
