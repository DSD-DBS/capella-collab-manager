/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { userEvent, within } from 'storybook/test';
import { MOBILE_VIEWPORT } from '../../.storybook/preview';
import { AppComponent } from './app.component';

const meta: Meta<AppComponent> = {
  title: 'General Components/App',
  component: AppComponent,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<AppComponent>;

export const ToggleNavbar: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockOwnUserWrapperServiceProvider(mockUser)],
    }),
  ],
  parameters: {
    layout: 'fullscreen',
    viewport: {
      defaultViewport: 'mobile1',
    },
    screenshot: {
      viewport: MOBILE_VIEWPORT,
      viewports: [],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const toggleNavbar = canvas.getByTestId('toggle-navbar');
    await userEvent.click(toggleNavbar);
  },
};
