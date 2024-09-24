/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { SettingsComponent } from './settings.component';

const meta: Meta<SettingsComponent> = {
  title: 'Settings Components/Overview',
  component: SettingsComponent,
};

export default meta;
type Story = StoryObj<SettingsComponent>;

export const General: Story = {
  args: {},
};
