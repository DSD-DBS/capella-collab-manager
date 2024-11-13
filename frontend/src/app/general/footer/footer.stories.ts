/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { mockAuthenticationWrapperServiceProvider } from 'src/storybook/auth';
import {
  mockFeedbackConfig,
  mockFeedbackWrapperServiceProvider,
} from 'src/storybook/feedback';
import { FooterComponent } from './footer.component';

const meta: Meta<FooterComponent> = {
  title: 'General Components/Footer',
  component: FooterComponent,
  parameters: {
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

export const WithFeedbackEnabled: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockFeedbackWrapperServiceProvider(mockFeedbackConfig),
        mockAuthenticationWrapperServiceProvider(),
      ],
    }),
  ],
};
