/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { userEvent, within } from 'storybook/test';
import { AddGitInstanceComponent } from './add-git-instance.component';

const meta: Meta<AddGitInstanceComponent> = {
  title: 'Settings Components/Modelsources/Git/Add Instance',
  component: AddGitInstanceComponent,
};

export default meta;
type Story = StoryObj<AddGitInstanceComponent>;

export const WithoutValues: Story = {
  args: {},
};

export const GeneralSelected: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    await userEvent.click(within(canvasElement).getByTestId('git-type'));

    const generalDropdownItem = document.querySelector(
      'mat-option[value="General"]',
    );
    if (!generalDropdownItem) {
      throw new Error('Dropdown item with value "General" not found');
    }
    await userEvent.click(generalDropdownItem);
  },
};

export const WithValues: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByTestId('git-type'));

    const githubDropdownItem = document.querySelector(
      'mat-option[value="GitHub"]',
    );
    if (!githubDropdownItem) {
      throw new Error('Dropdown item with value "GitHub" not found');
    }
    await userEvent.click(githubDropdownItem);

    await userEvent.type(canvas.getByTestId('name'), 'GitHub');
    await userEvent.type(canvas.getByTestId('url'), 'https://github.com');
    await userEvent.type(
      canvas.getByTestId('api_url'),
      'https://api.github.com',
    );
  },
};
