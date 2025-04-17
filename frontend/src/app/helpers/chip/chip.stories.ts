/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { ChipComponent } from './chip.component';

const meta: Meta<ChipComponent> = {
  title: 'Helpers/Chip',
  component: ChipComponent,
};

export default meta;
type Story = StoryObj<ChipComponent>;

export const Example: Story = {
  args: {},
  render: (args) => ({
    props: args,
    template: `
      <app-chip>Example Chip</app-chip>
    `,
  }),
};
