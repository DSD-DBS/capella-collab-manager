/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { FeedbackWrapperService } from 'src/app/sessions/feedback/feedback.service';
import { MockAuthenticationWrapperService } from 'src/storybook/auth';
import {
  mockFeedbackConfig,
  MockFeedbackWrapperService,
} from 'src/storybook/feedback';
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

export const WithFeedbackEnabled: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: FeedbackWrapperService,
          useFactory: () => new MockFeedbackWrapperService(mockFeedbackConfig),
        },
        {
          provide: AuthenticationWrapperService,
          useFactory: () => new MockAuthenticationWrapperService(),
        },
      ],
    }),
  ],
};
