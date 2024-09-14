/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { FooterComponent } from './footer.component';

const meta: Meta<FooterComponent> = {
  title: 'General Components/Footer',
  component: FooterComponent,
  parameters: {
    chromatic: { viewports: [430, 1920] },
    screenshot: {
      viewports: {
        mobile: {
          width: 430,
        },
      },
    },
  },
};

export default meta;
type Story = StoryObj<FooterComponent>;

export const General: Story = {
  args: {},
};
