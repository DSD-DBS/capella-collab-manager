/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import {
  mockNotice,
  mockNoticeWrapperServiceProvider,
} from 'src/storybook/notices';
import { AlertSettingsComponent } from './alert-settings.component';

const meta: Meta<AlertSettingsComponent> = {
  title: 'Settings Components/Alert Settings',
  component: AlertSettingsComponent,
};

export default meta;
type Story = StoryObj<AlertSettingsComponent>;

export const Loading: Story = {
  args: {},
};

export const NoAlerts: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockNoticeWrapperServiceProvider([])],
    }),
  ],
};

export const SomeAlerts: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockNoticeWrapperServiceProvider([
          mockNotice,
          { ...mockNotice, id: 2 },
        ]),
      ],
    }),
  ],
};

export const AlertExpanded: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockNoticeWrapperServiceProvider([mockNotice])],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const alert = canvas.getByTestId('alert-1');
    await userEvent.click(alert);
  },
};
