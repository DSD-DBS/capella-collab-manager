/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { DisplayValueComponent } from './display-value.component';

const meta: Meta<DisplayValueComponent> = {
  title: 'Helpers/Display Value',
  component: DisplayValueComponent,
};

export default meta;
type Story = StoryObj<DisplayValueComponent>;

export const Normal: Story = {
  args: {
    valueName: 'Normal Value',
    value: 'value',
    blurValue: false,
  },
};

export const Blurred: Story = {
  args: {
    valueName: 'Blurred Value',
    value: 'blurred value',
    blurValue: true,
  },
};
