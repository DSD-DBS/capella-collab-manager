/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { EditProjectMetadataComponent } from './edit-project-metadata.component';

const meta: Meta<EditProjectMetadataComponent> = {
  title: 'Project Components/Project Details/Edit Project Metadata',
  component: EditProjectMetadataComponent,
};

export default meta;
type Story = StoryObj<EditProjectMetadataComponent>;

export const General: Story = {
  args: {},
};

export const WithTitle: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const nameInput = canvas.getByTestId('name-input');
    await userEvent.type(nameInput, 'Name');
  },
};
